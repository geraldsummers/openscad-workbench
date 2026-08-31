from __future__ import annotations

import argparse
import base64
import hashlib
import json
import math
import os
import re
import shlex
import shutil
import socket
import subprocess
import sys
import tempfile
import textwrap
import time
import tomllib
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

import manifold3d
import numpy as np
from PIL import Image, ImageDraw
import trimesh

from . import __version__


WORKBENCH = Path.home() / "openscad-workbench"
MODELS = WORKBENCH / "models"
TMP_ROOT = Path.home() / ".tmp"
DEFAULT_ENVELOPE = np.array([270.0, 270.0, 256.0])
DEFAULT_TOLERANCE = 0.01
FAILURE_PATTERN = re.compile(
    r"(^|\n)\s*(ERROR|WARNING):|Current top level object is (empty|not a 3d object)",
    re.IGNORECASE,
)


@dataclass
class Check:
    name: str
    passed: bool
    actual: Any
    expected: Any


class UserError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def command_env() -> dict[str, str]:
    env = os.environ.copy()
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    env["TMPDIR"] = str(TMP_ROOT)
    env.setdefault("LIBGL_ALWAYS_SOFTWARE", "1")
    return env


def run(command: Sequence[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        cwd=cwd,
        env=command_env(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def combined_digest(paths: Sequence[Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths, key=lambda item: item.name):
        digest.update(path.name.encode())
        digest.update(bytes.fromhex(sha256_file(path)))
    return digest.hexdigest()


def mesh_geometry_digest(mesh: trimesh.Trimesh) -> str:
    """Hash geometry independently of mesh file ordering and metadata."""
    triangles = np.round(np.asarray(mesh.triangles, dtype=np.float64), decimals=7)
    normalized: list[tuple[float, ...]] = []
    for triangle in triangles:
        vertices = sorted(tuple(float(value) for value in vertex) for vertex in triangle)
        normalized.append(tuple(value for vertex in vertices for value in vertex))
    normalized.sort()
    canonical = np.asarray(normalized, dtype="<f8")
    return hashlib.sha256(canonical.tobytes()).hexdigest()


def resolve_model(value: str) -> Path:
    supplied = Path(value).expanduser()
    candidates = [supplied, Path.cwd() / supplied, MODELS / value]
    for candidate in candidates:
        if candidate.is_dir() and (candidate / "model.toml").is_file():
            return candidate.resolve()
    raise UserError(f"Model not found: {value}")


def read_config(model_dir: Path) -> dict[str, Any]:
    with (model_dir / "model.toml").open("rb") as stream:
        config = tomllib.load(stream)
    if config.get("schema_version") != 2:
        raise UserError("model.toml must use schema_version = 2; migrate requirements before verifying")
    if config.get("units") != "mm":
        raise UserError("model.toml must set units = \"mm\"")
    source_name = config.get("source", "model.scad")
    source = model_dir / source_name
    if not source.is_file():
        raise UserError(f"OpenSCAD source does not exist: {source}")
    geometry = config.setdefault("geometry", {})
    if geometry.get("connected_components", 1) != 1:
        raise UserError("This workbench requires connected_components = 1")
    requirements = config.get("requirements")
    if not isinstance(requirements, list) or not requirements:
        raise UserError("model.toml must declare at least one [[requirements]] entry")
    ids: set[str] = set()
    spec = (model_dir / "spec.md").read_text()
    for requirement in requirements:
        requirement_id = requirement.get("id")
        if not isinstance(requirement_id, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", requirement_id):
            raise UserError("Every requirement needs a lowercase id")
        if requirement_id in ids:
            raise UserError(f"Duplicate requirement id: {requirement_id}")
        ids.add(requirement_id)
        if f"[{requirement_id}]" not in spec:
            raise UserError(f"spec.md must reference requirement [{requirement_id}]")
        method = requirement.get("method")
        if method not in {"source", "mesh", "visual"}:
            raise UserError(f"Requirement {requirement_id} has unknown method {method!r}")
        if not str(requirement.get("description", "")).strip():
            raise UserError(f"Requirement {requirement_id} needs a description")
        if method == "mesh" and requirement.get("kind") not in {
            "extents", "bounds", "volume", "surface_area", "center_mass", "symmetry", "region", "section"
        }:
            raise UserError(f"Requirement {requirement_id} has unknown mesh kind")
        if method == "visual":
            views = requirement.get("views")
            if not isinstance(views, list) or not views or any(view not in PREVIEW_VIEWS for view in views):
                raise UserError(f"Visual requirement {requirement_id} needs valid views")
    spec_ids = set(re.findall(r"(?m)^\s*-\s+\[([a-z0-9][a-z0-9-]*)\]", spec))
    if spec_ids != ids:
        missing = sorted(spec_ids - ids)
        raise UserError(f"spec.md contains unmapped requirement IDs: {', '.join(missing)}")
    return config


def openscad_base(source: Path) -> list[str]:
    return [
        "openscad",
        "--backend=Manifold",
        "--hardwarnings",
        "--check-parameters=true",
        "--check-parameter-ranges=true",
        str(source),
    ]


def export_geometry(source: Path, build_dir: Path) -> tuple[subprocess.CompletedProcess[str], list[Path]]:
    stl = build_dir / "model.stl"
    three_mf = build_dir / "model.3mf"
    summary = build_dir / "openscad-summary.json"
    deps = build_dir / "dependencies.d"
    for artifact in (stl, three_mf, summary, deps):
        artifact.unlink(missing_ok=True)
    command = openscad_base(source)
    command[1:1] = [
        "--enable=predictible-output",
        "--summary=all",
        f"--summary-file={summary}",
        "-d",
        str(deps),
        "-o",
        str(stl),
        "-o",
        str(three_mf),
    ]
    result = run(command, cwd=source.parent)
    (build_dir / "openscad.log").write_text(result.stdout + result.stderr)
    return result, [stl, three_mf]


def load_mesh(path: Path) -> trimesh.Trimesh:
    loaded = trimesh.load(path, force="scene", process=False)
    if isinstance(loaded, trimesh.Scene):
        geometries = [geometry for geometry in loaded.geometry.values() if len(geometry.faces)]
        if not geometries:
            raise UserError(f"No mesh geometry in {path.name}")
        mesh = trimesh.util.concatenate(geometries)
    elif isinstance(loaded, trimesh.Trimesh):
        mesh = loaded
    else:
        raise UserError(f"Unsupported geometry in {path.name}: {type(loaded).__name__}")
    # STL repeats coordinates for each triangle. Weld exact duplicates before
    # topology checks so connectivity reflects the solid, not file encoding.
    mesh.merge_vertices(digits_vertex=8)
    return mesh


def manifold_status(mesh: trimesh.Trimesh) -> str:
    return str(to_manifold(mesh).status())


def to_manifold(mesh: trimesh.Trimesh) -> manifold3d.Manifold:
    manifold_mesh = manifold3d.Mesh(
        vert_properties=np.ascontiguousarray(mesh.vertices, dtype=np.float32),
        tri_verts=np.ascontiguousarray(mesh.faces, dtype=np.uint32),
    )
    return manifold3d.Manifold(manifold_mesh)


def mesh_metrics(mesh: trimesh.Trimesh) -> dict[str, Any]:
    bounds = np.asarray(mesh.bounds, dtype=float)
    edge_uses = np.bincount(mesh.edges_unique_inverse, minlength=len(mesh.edges_unique))
    referenced = np.unique(mesh.faces.reshape(-1))
    return {
        "vertices": int(len(mesh.vertices)),
        "faces": int(len(mesh.faces)),
        "bounds_mm": bounds.tolist(),
        "extents_mm": np.asarray(mesh.extents, dtype=float).tolist(),
        "volume_mm3": float(mesh.volume),
        "surface_area_mm2": float(mesh.area),
        "center_mass_mm": np.asarray(mesh.center_mass, dtype=float).tolist(),
        "euler_number": int(mesh.euler_number),
        "genus": int(max(0, (2 - int(mesh.euler_number)) // 2)) if mesh.is_watertight else None,
        "boundary_edges": int(np.count_nonzero(edge_uses == 1)),
        "nonmanifold_edges": int(np.count_nonzero(edge_uses > 2)),
        "isolated_vertices": int(len(mesh.vertices) - len(referenced)),
        "body_count": int(mesh.body_count),
        "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "all_finite": bool(np.isfinite(mesh.vertices).all()),
        "all_faces_unique": bool(mesh.unique_faces().all()),
        "all_faces_nondegenerate": bool(mesh.nondegenerate_faces().all()),
        "manifold_status": manifold_status(mesh),
        "geometry_sha256": mesh_geometry_digest(mesh),
    }


def add_mesh_checks(
    checks: list[Check],
    label: str,
    metrics: dict[str, Any],
    envelope: np.ndarray,
    tolerance: float,
) -> None:
    extents = np.asarray(metrics["extents_mm"])
    bounds = np.asarray(metrics["bounds_mm"])
    checks.extend(
        [
            Check(f"{label}.nonempty", metrics["faces"] > 0, metrics["faces"], "> 0 faces"),
            Check(f"{label}.finite", metrics["all_finite"], metrics["all_finite"], True),
            Check(f"{label}.watertight", metrics["watertight"], metrics["watertight"], True),
            Check(
                f"{label}.winding_consistent",
                metrics["winding_consistent"],
                metrics["winding_consistent"],
                True,
            ),
            Check(f"{label}.positive_volume", metrics["volume_mm3"] > 0, metrics["volume_mm3"], "> 0 mm^3"),
            Check(f"{label}.one_body", metrics["body_count"] == 1, metrics["body_count"], 1),
            Check(f"{label}.boundary_edges", metrics["boundary_edges"] == 0, metrics["boundary_edges"], 0),
            Check(f"{label}.nonmanifold_edges", metrics["nonmanifold_edges"] == 0, metrics["nonmanifold_edges"], 0),
            Check(f"{label}.isolated_vertices", metrics["isolated_vertices"] == 0, metrics["isolated_vertices"], 0),
            Check(
                f"{label}.unique_faces",
                metrics["all_faces_unique"],
                metrics["all_faces_unique"],
                True,
            ),
            Check(
                f"{label}.nondegenerate_faces",
                metrics["all_faces_nondegenerate"],
                metrics["all_faces_nondegenerate"],
                True,
            ),
            Check(
                f"{label}.manifold3d",
                metrics["manifold_status"] == "Error.NoError",
                metrics["manifold_status"],
                "Error.NoError",
            ),
            Check(
                f"{label}.touches_z0",
                abs(float(bounds[0, 2])) <= tolerance,
                float(bounds[0, 2]),
                f"0 +/- {tolerance} mm",
            ),
            Check(
                f"{label}.build_envelope",
                bool(np.all(extents <= envelope + tolerance)),
                extents.tolist(),
                f"<= {envelope.tolist()} mm",
            ),
        ]
    )


def compare_meshes(
    checks: list[Check],
    stl: dict[str, Any],
    three_mf: dict[str, Any],
    tolerance: float,
    stl_mesh: trimesh.Trimesh | None = None,
    three_mf_mesh: trimesh.Trimesh | None = None,
) -> None:
    stl_bounds = np.asarray(stl["bounds_mm"])
    mf_bounds = np.asarray(three_mf["bounds_mm"])
    bounds_match = bool(np.allclose(stl_bounds, mf_bounds, atol=tolerance, rtol=1e-6))
    volume_match = math.isclose(
        stl["volume_mm3"],
        three_mf["volume_mm3"],
        abs_tol=tolerance,
        rel_tol=1e-5,
    )
    checks.extend(
        [
            Check("exports.bounds_agree", bounds_match, [stl_bounds.tolist(), mf_bounds.tolist()], f"within {tolerance} mm"),
            Check(
                "exports.volume_agrees",
                volume_match,
                [stl["volume_mm3"], three_mf["volume_mm3"]],
                "within 0.001% or absolute tolerance",
            ),
        ]
    )
    if stl_mesh is not None and three_mf_mesh is not None:
        first, second = to_manifold(stl_mesh), to_manifold(three_mf_mesh)
        difference = float((first - second).volume() + (second - first).volume())
        ratio = difference / max(abs(float(first.volume())), tolerance)
        checks.append(Check("exports.symmetric_difference", ratio <= 1e-6, ratio, "<= 1e-6 of STL volume"))


def numeric_check(name: str, actual: Any, expected: Any, tolerance: float) -> Check:
    actual_array = np.asarray(actual, dtype=float)
    expected_array = np.asarray(expected, dtype=float)
    passed = actual_array.shape == expected_array.shape and bool(
        np.allclose(actual_array, expected_array, atol=tolerance, rtol=0)
    )
    return Check(name, passed, actual, {"value": expected, "tolerance": tolerance})


def region_manifold(requirement: dict[str, Any]) -> manifold3d.Manifold:
    shape = requirement.get("shape")
    center = requirement.get("center")
    if not isinstance(center, list) or len(center) != 3:
        raise UserError(f"Region requirement {requirement['id']} needs center = [x, y, z]")
    if shape == "box":
        size = requirement.get("size")
        if not isinstance(size, list) or len(size) != 3 or any(float(value) <= 0 for value in size):
            raise UserError(f"Region requirement {requirement['id']} needs positive box size")
        return manifold3d.Manifold.cube(tuple(map(float, size)), True).translate(tuple(map(float, center)))
    if shape == "cylinder":
        radius, height = requirement.get("radius"), requirement.get("height")
        if not isinstance(radius, (int, float)) or not isinstance(height, (int, float)) or radius <= 0 or height <= 0:
            raise UserError(f"Region requirement {requirement['id']} needs positive radius and height")
        region = manifold3d.Manifold.cylinder(float(height), float(radius), circular_segments=96, center=True)
        axis = requirement.get("axis", "z")
        if axis == "x":
            region = region.rotate((0, 90, 0))
        elif axis == "y":
            region = region.rotate((-90, 0, 0))
        elif axis != "z":
            raise UserError(f"Region requirement {requirement['id']} axis must be x, y, or z")
        return region.translate(tuple(map(float, center)))
    raise UserError(f"Region requirement {requirement['id']} shape must be box or cylinder")


def section_metrics(mesh: trimesh.Trimesh, axis: str, offset: float) -> dict[str, Any]:
    axis_index = {"x": 0, "y": 1, "z": 2}.get(axis)
    if axis_index is None:
        raise UserError("Section axis must be x, y, or z")
    normal = np.zeros(3)
    origin = np.zeros(3)
    normal[axis_index] = 1
    origin[axis_index] = offset
    section = mesh.section(plane_origin=origin, plane_normal=normal)
    if section is None:
        return {"components": 0, "area_mm2": 0.0, "bounds_mm": None}
    dimensions = [index for index in range(3) if index != axis_index]
    loops = [np.asarray(loop)[:, dimensions] for loop in section.discrete]
    areas = [abs(float(np.dot(loop[:, 0], np.roll(loop[:, 1], -1)) - np.dot(loop[:, 1], np.roll(loop[:, 0], -1)))) / 2 for loop in loops]
    points = np.vstack(loops)
    return {"components": len(loops), "area_mm2": float(sum(areas)), "bounds_mm": [points.min(axis=0).tolist(), points.max(axis=0).tolist()]}


def evaluate_requirements(
    requirements: Sequence[dict[str, Any]], mesh: trimesh.Trimesh, metrics: dict[str, Any], export_log: str
) -> list[Check]:
    checks: list[Check] = []
    solid = to_manifold(mesh)
    metric_keys = {
        "extents": "extents_mm", "bounds": "bounds_mm", "volume": "volume_mm3",
        "surface_area": "surface_area_mm2", "center_mass": "center_mass_mm",
    }
    for requirement in requirements:
        requirement_id = requirement["id"]
        name = f"requirement.{requirement_id}"
        method = requirement["method"]
        if method == "visual":
            continue
        if method == "source":
            marker = f"SCADCTL_REQUIREMENT:{requirement_id}:PASS"
            checks.append(Check(name, marker in export_log, marker if marker in export_log else None, marker))
            continue
        kind = requirement["kind"]
        tolerance = requirement.get("tolerance")
        if kind in metric_keys:
            if tolerance is None or "expected" not in requirement:
                raise UserError(f"Mesh requirement {requirement_id} needs expected and tolerance")
            checks.append(numeric_check(name, metrics[metric_keys[kind]], requirement["expected"], float(tolerance)))
        elif kind == "symmetry":
            axis = requirement.get("axis")
            offset = float(requirement.get("offset", 0))
            tolerance = requirement.get("max_difference_ratio")
            if axis not in {"x", "y", "z"} or tolerance is None:
                raise UserError(f"Symmetry requirement {requirement_id} needs axis and max_difference_ratio")
            index = {"x": 0, "y": 1, "z": 2}[axis]
            shift = [0.0, 0.0, 0.0]
            shift[index] = -offset
            normal = [0.0, 0.0, 0.0]
            normal[index] = 1.0
            mirrored = solid.translate(tuple(shift)).mirror(tuple(normal)).translate(tuple(-v for v in shift))
            difference = float((solid - mirrored).volume() + (mirrored - solid).volume())
            ratio = difference / max(abs(float(solid.volume())), DEFAULT_TOLERANCE)
            checks.append(Check(name, ratio <= float(tolerance), ratio, {"max_difference_ratio": tolerance}))
        elif kind == "region":
            region = region_manifold(requirement)
            fraction = float((solid ^ region).volume() / region.volume())
            expected = requirement.get("expected")
            threshold = requirement.get("min_fraction" if expected == "solid" else "max_fraction")
            if expected not in {"solid", "void"} or threshold is None:
                raise UserError(f"Region requirement {requirement_id} needs expected and fraction threshold")
            passed = fraction >= float(threshold) if expected == "solid" else fraction <= float(threshold)
            checks.append(Check(name, passed, fraction, {expected: threshold}))
        elif kind == "section":
            actual = section_metrics(mesh, requirement.get("axis", "z"), float(requirement.get("offset", 0)))
            expected = requirement.get("expected")
            tolerance = requirement.get("tolerance")
            if not isinstance(expected, dict) or tolerance is None:
                raise UserError(f"Section requirement {requirement_id} needs expected table and tolerance")
            passed = actual["components"] == expected.get("components")
            for key in ("area_mm2", "bounds_mm"):
                if key in expected:
                    passed = passed and numeric_check(name, actual[key], expected[key], float(tolerance)).passed
            checks.append(Check(name, passed, actual, {**expected, "tolerance": tolerance}))
    return checks


def check_expected_extents(checks: list[Check], metrics: dict[str, Any], geometry: dict[str, Any]) -> None:
    expected = geometry.get("expected_extents_mm")
    if expected is None:
        return
    expected_array = np.asarray(expected, dtype=float)
    if expected_array.shape != (3,):
        raise UserError("geometry.expected_extents_mm must contain exactly three numbers")
    tolerance = float(geometry.get("expected_extents_tolerance_mm", DEFAULT_TOLERANCE))
    actual = np.asarray(metrics["extents_mm"])
    checks.append(
        Check(
            "model.expected_extents",
            bool(np.allclose(actual, expected_array, atol=tolerance, rtol=0)),
            actual.tolist(),
            f"{expected_array.tolist()} +/- {tolerance} mm",
        )
    )


PREVIEW_VIEWS = {
    "front": "0,0,0,90,0,0,200",
    "rear": "0,0,0,90,0,180,200",
    "left": "0,0,0,90,0,270,200",
    "right": "0,0,0,90,0,90,200",
    "top": "0,0,0,0,0,0,200",
    "bottom": "0,0,0,180,0,0,200",
    "isometric-front": "0,0,0,55,0,25,200",
    "isometric-rear": "0,0,0,55,0,205,200",
    "isometric-underside-front": "0,0,0,125,0,25,200",
    "isometric-underside-rear": "0,0,0,125,0,205,200",
}
PREVIEW_SIZE = (1600, 1200)
PREVIEW_XVFB_SCREEN = "1920x1440x24"
CONTACT_SHEET_COLUMNS = 4
CONTACT_SHEET_IMAGE_SIZE = (800, 600)
CONTACT_SHEET_TITLE_HEIGHT = 40
PRESENTATION_VIEW_LABELS = {
    "isometric-front": "Isometric Front",
    "isometric-rear": "Isometric Rear",
    "isometric-underside-front": "Isometric Underside Front",
    "isometric-underside-rear": "Isometric Underside Rear",
    "front": "Front",
    "rear": "Rear",
    "left": "Left",
    "right": "Right",
    "top": "Top",
    "bottom": "Bottom",
}
PRESENTATION_TEXT_TABS = ("Spec", "Report", "Source")
PRESENTATION_TABS = (*PRESENTATION_VIEW_LABELS.values(), *PRESENTATION_TEXT_TABS)


def render_previews(source: Path, preview_dir: Path) -> tuple[list[Path], list[str]]:
    preview_dir.mkdir(parents=True, exist_ok=True)
    for stale in preview_dir.glob("*.png"):
        stale.unlink()
    images: list[Path] = []
    failures: list[str] = []
    for name, camera in PREVIEW_VIEWS.items():
        output = preview_dir / f"{name}.png"
        output.unlink(missing_ok=True)
        command = [
            "xvfb-run",
            "-a",
            "-s",
            f"-screen 0 {PREVIEW_XVFB_SCREEN}",
            "openscad",
            "--backend=Manifold",
            "--hardwarnings",
            "--render=true",
            "--autocenter",
            "--viewall",
            "--projection=ortho",
            f"--imgsize={PREVIEW_SIZE[0]},{PREVIEW_SIZE[1]}",
            "--colorscheme=Tomorrow Night",
            f"--camera={camera}",
            "-o",
            str(output),
            str(source),
        ]
        result = run(command, cwd=source.parent)
        (preview_dir / f"{name}.log").write_text(result.stdout + result.stderr)
        if result.returncode or FAILURE_PATTERN.search(result.stdout + result.stderr) or not output.is_file():
            failures.append(f"{name}: OpenSCAD exited {result.returncode}")
        else:
            images.append(output)
    return images, failures


def image_metrics(path: Path) -> dict[str, Any]:
    image = Image.open(path).convert("RGB")
    pixels = np.asarray(image)
    background = pixels[0, 0].astype(int)
    foreground = np.max(np.abs(pixels.astype(int) - background), axis=2) > 12
    locations = np.argwhere(foreground)
    occupancy = float(np.mean(foreground))
    clipped = bool(
        len(locations)
        and (locations[:, 0].min() == 0 or locations[:, 1].min() == 0
             or locations[:, 0].max() == pixels.shape[0] - 1 or locations[:, 1].max() == pixels.shape[1] - 1)
    )
    return {"size": list(image.size), "foreground_fraction": occupancy, "clipped": clipped, "sha256": sha256_file(path)}


def add_image_checks(checks: list[Check], images: Sequence[Path]) -> dict[str, Any]:
    metrics = {path.stem: image_metrics(path) for path in images}
    expected_size = list(PREVIEW_SIZE)
    for name, item in metrics.items():
        checks.extend([
            Check(f"preview.{name}.size", item["size"] == expected_size, item["size"], expected_size),
            Check(f"preview.{name}.foreground", 0.01 <= item["foreground_fraction"] <= 0.90, item["foreground_fraction"], "0.01..0.90"),
            Check(f"preview.{name}.not_clipped", not item["clipped"], item["clipped"], False),
        ])
    unique = len({item["sha256"] for item in metrics.values()})
    checks.append(Check("previews.not_all_duplicates", unique > 1, unique, "> 1 unique image"))
    return metrics


def create_contact_sheet(images: Sequence[Path], output: Path) -> None:
    if len(images) != len(PREVIEW_VIEWS):
        raise UserError("Cannot build a contact sheet without all preview views")
    tile_size = (CONTACT_SHEET_IMAGE_SIZE[0], CONTACT_SHEET_IMAGE_SIZE[1] + CONTACT_SHEET_TITLE_HEIGHT)
    rows = math.ceil(len(images) / CONTACT_SHEET_COLUMNS)
    sheet = Image.new(
        "RGB",
        (tile_size[0] * CONTACT_SHEET_COLUMNS, tile_size[1] * rows),
        "#111827",
    )
    draw = ImageDraw.Draw(sheet)
    for index, image_path in enumerate(images):
        with Image.open(image_path) as source:
            image = source.convert("RGB").resize(CONTACT_SHEET_IMAGE_SIZE, Image.Resampling.LANCZOS)
        x = (index % CONTACT_SHEET_COLUMNS) * tile_size[0]
        y = (index // CONTACT_SHEET_COLUMNS) * tile_size[1]
        sheet.paste(image, (x, y + CONTACT_SHEET_TITLE_HEIGHT))
        draw.text((x + 16, y + 12), image_path.stem.upper(), fill="white")
    sheet.save(output)


def report_markdown(report: dict[str, Any]) -> str:
    icon = "PASS" if report["technical_pass"] else "FAIL"
    lines = [
        f"# Verification: {report['model']}",
        "",
        f"Technical result: **{icon}**",
        "",
        f"Visual review: **{report['visual_review']['status'].upper()}**",
        "",
        f"Presentation: **{report.get('presentation', {}).get('status', 'missing').upper()}**",
        "",
        "## Checks",
        "",
        "| Check | Result | Actual | Expected |",
        "|---|---:|---|---|",
    ]
    for check in report["checks"]:
        actual = json.dumps(check["actual"], separators=(",", ":"))
        expected = json.dumps(check["expected"], separators=(",", ":"))
        lines.append(f"| `{check['name']}` | {'PASS' if check['passed'] else 'FAIL'} | {actual} | {expected} |")
    review = report.get("visual_review", {})
    if review.get("requirements"):
        lines.extend(["", "## Visual evidence", "", "| Requirement | Verdict | Views | Observations |", "|---|---:|---|---|"])
        for item in review["requirements"]:
            observations = str(item.get("observations", "")).replace("|", "\\|")
            lines.append(f"| `{item['id']}` | {item['verdict'].upper()} | {', '.join(item['evidence_views'])} | {observations} |")
    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            "- `model.stl`",
            "- `model.3mf`",
            "- `previews/contact-sheet.png`",
            "- `report.json`",
            "",
        ]
    )
    presentation = report.get("presentation", {})
    if presentation.get("workspace_id"):
        lines.extend(
            [
                "## Herdr presentation",
                "",
                f"- Workspace: `{presentation['workspace_id']}` ({presentation.get('workspace_label', '')})",
                *[
                    f"- {label}: tab `{item['tab_id']}`, pane `{item['pane_id']}`"
                    for label, item in presentation.get("tabs", {}).items()
                ],
                "",
            ]
        )
    return "\n".join(lines)


def presentation_for_digest(build_dir: Path, artifact_digest: str | None) -> dict[str, Any]:
    path = build_dir / "presentation.json"
    if not path.is_file():
        return {"status": "missing", "artifact_digest": None}
    presentation = json.loads(path.read_text())
    native_previews = presentation.get("native_previews", {})
    all_views_native = set(native_previews) == set(PRESENTATION_VIEW_LABELS.values()) and all(
        all(item.get("cell_size_px", [])) for item in native_previews.values()
    )
    presentation["status"] = "presented" if (
        presentation.get("artifact_digest") == artifact_digest
        and presentation.get("preview_mode") == "native-herdr"
        and all_views_native
    ) else "stale"
    return presentation


def inspection_template(requirements: Sequence[dict[str, Any]], artifact_digest: str | None) -> dict[str, Any]:
    return {
        "schema_version": 2,
        "artifact_digest": artifact_digest,
        "reviewer": {"kind": "agent"},
        "views": [
            {"id": view, "verdict": None, "observations": ""}
            for view in PREVIEW_VIEWS
        ],
        "requirements": [
            {
                "id": requirement["id"],
                "verdict": None,
                "evidence_views": requirement["views"],
                "observations": "",
                "confidence": None,
            }
            for requirement in requirements if requirement["method"] == "visual"
        ],
    }


def verify_model(model_dir: Path) -> dict[str, Any]:
    config = read_config(model_dir)
    source = model_dir / config.get("source", "model.scad")
    geometry = config["geometry"]
    envelope = np.asarray(geometry.get("max_extents_mm", DEFAULT_ENVELOPE.tolist()), dtype=float)
    if envelope.shape != (3,):
        raise UserError("geometry.max_extents_mm must contain exactly three numbers")
    tolerance = float(geometry.get("z0_tolerance_mm", DEFAULT_TOLERANCE))
    build_dir = model_dir / "build"
    preview_dir = build_dir / "previews"
    build_dir.mkdir(parents=True, exist_ok=True)
    preview_dir.mkdir(parents=True, exist_ok=True)

    checks: list[Check] = []
    export_result, artifacts = export_geometry(source, build_dir)
    export_log = export_result.stdout + export_result.stderr
    export_ok = export_result.returncode == 0 and not FAILURE_PATTERN.search(export_log)
    artifacts_ok = all(path.is_file() and path.stat().st_size > 0 for path in artifacts)
    checks.append(Check("openscad.clean_export", export_ok, export_result.returncode, 0))
    checks.append(Check("openscad.artifacts_created", artifacts_ok, artifacts_ok, True))

    metrics: dict[str, Any] = {}
    meshes: dict[str, trimesh.Trimesh] = {}
    if export_ok and artifacts_ok:
        for artifact in artifacts:
            label = artifact.suffix.lstrip(".")
            mesh = load_mesh(artifact)
            meshes[label] = mesh
            item_metrics = mesh_metrics(mesh)
            metrics[label] = item_metrics
            add_mesh_checks(checks, label, item_metrics, envelope, tolerance)
        compare_meshes(checks, metrics["stl"], metrics["3mf"], tolerance, meshes["stl"], meshes["3mf"])
        check_expected_extents(checks, metrics["stl"], geometry)
        checks.extend(evaluate_requirements(config["requirements"], meshes["stl"], metrics["stl"], export_log))

    images, preview_failures = render_previews(source, preview_dir) if export_ok else ([], ["export failed"])
    contact_sheet = preview_dir / "contact-sheet.png"
    if not preview_failures:
        create_contact_sheet(images, contact_sheet)
    preview_ok = not preview_failures and contact_sheet.is_file()
    checks.append(Check("previews.complete", preview_ok, preview_failures or len(images), len(PREVIEW_VIEWS)))
    preview_metrics = add_image_checks(checks, images) if preview_ok else {}

    source_paths = [source, model_dir / "model.toml", model_dir / "spec.md"]
    source_digest = combined_digest([path for path in source_paths if path.is_file()])
    technical_pass = all(check.passed for check in checks)
    artifact_digest = None
    if "stl" in metrics and "3mf" in metrics:
        review_binding = {
            "source_sha256": source_digest,
            "stl_geometry_sha256": metrics["stl"]["geometry_sha256"],
            "3mf_geometry_sha256": metrics["3mf"]["geometry_sha256"],
            "preview_sha256": {name: item["sha256"] for name, item in sorted(preview_metrics.items())},
        }
        artifact_digest = hashlib.sha256(
            json.dumps(review_binding, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()

    review_file = build_dir / "review.json"
    review = {"schema_version": 2, "status": "pending", "artifact_digest": None}
    if review_file.is_file():
        existing = json.loads(review_file.read_text())
        if existing.get("schema_version") == 2 and existing.get("artifact_digest") == artifact_digest:
            review = existing
        else:
            review["status"] = "stale"

    version_result = run(["openscad", "--version"])
    report = {
        "schema_version": 2,
        "model": config.get("name", model_dir.name),
        "generated_at": utc_now(),
        "technical_pass": technical_pass,
        "visual_review": review,
        "presentation": presentation_for_digest(build_dir, artifact_digest),
        "artifact_digest": artifact_digest,
        "artifact_files": {
            path.relative_to(build_dir).as_posix(): sha256_file(path)
            for path in [*artifacts, contact_sheet]
            if path.is_file()
        },
        "source_digest": source_digest,
        "tool_versions": {
            "scadctl": __version__,
            "openscad": (version_result.stdout + version_result.stderr).strip(),
            "bosl2": "2.0.752 (5b1f7b2d4344b75265324309e11c3c8e7f5cbb8b)",
            "trimesh": trimesh.__version__,
        },
        "metrics": metrics,
        "preview_metrics": preview_metrics,
        "requirements": config["requirements"],
        "checks": [asdict(check) for check in checks],
    }
    template = inspection_template(config["requirements"], artifact_digest)
    (build_dir / "inspection-template.json").write_text(json.dumps(template, indent=2, sort_keys=True) + "\n")
    (build_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    (build_dir / "report.md").write_text(report_markdown(report))
    return report


def scaffold(name: str) -> Path:
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", name):
        raise UserError("Model names use lowercase letters, digits, and hyphens")
    model_dir = MODELS / name
    if model_dir.exists():
        raise UserError(f"Model already exists: {model_dir}")
    model_dir.mkdir(parents=True)
    (model_dir / "model.scad").write_text(
        textwrap.dedent(
            """\
            include <BOSL2/std.scad>

            width = 40;
            depth = 30;
            height = 12;
            corner_radius = 2;

            assert(width > 0 && depth > 0 && height > 0, "Dimensions must be positive");
            assert(corner_radius >= 0 && corner_radius <= min(width, depth) / 2,
                   "Corner radius must fit the footprint");

            cuboid([width, depth, height], rounding=corner_radius, edges="Z", anchor=BOTTOM, $fn=48);
            """
        )
    )
    (model_dir / "model.toml").write_text(
        textwrap.dedent(
            f"""\
            schema_version = 2
            name = "{name}"
            source = "model.scad"
            units = "mm"

            [geometry]
            connected_components = 1
            max_extents_mm = [270.0, 270.0, 256.0]
            z0_tolerance_mm = 0.01
            expected_extents_mm = [40.0, 30.0, 12.0]
            expected_extents_tolerance_mm = 0.01

            [[requirements]]
            id = "overall-size"
            description = "Overall dimensions are 40 x 30 x 12 mm"
            method = "mesh"
            kind = "extents"
            expected = [40.0, 30.0, 12.0]
            tolerance = 0.01

            [[requirements]]
            id = "positive-dimensions"
            description = "Named dimensions and corner radius obey their constraints"
            method = "source"

            [[requirements]]
            id = "intended-shape"
            description = "The result is one upright rounded rectangular block without unintended features"
            method = "visual"
            views = ["front", "rear", "left", "right", "top", "bottom", "isometric-front", "isometric-rear", "isometric-underside-front", "isometric-underside-rear"]
            """
        )
    )
    (model_dir / "spec.md").write_text(
        textwrap.dedent(
            f"""\
            # {name} specification

            ## Requirements

            - [overall-size] Overall dimensions are mesh-verified.
            - [positive-dimensions] Parameter relationships are source-verified.
            - [intended-shape] Shape and orientation are visually verified in all ten views.

            ## Exclusions

            Slicing, material, nozzle, support, overhang, and toolpath assessment are out of scope.
            """
        )
    )
    return model_dir


def doctor() -> bool:
    results: list[tuple[str, bool, str]] = []
    version = run(["openscad", "--version"])
    version_text = (version.stdout + version.stderr).strip()
    results.append(("OpenSCAD 2026.08.30", version.returncode == 0 and "2026.08.30" in version_text, version_text))
    bosl_version = Path.home() / ".local/share/OpenSCAD/libraries/BOSL2/version.scad"
    bosl_ok = bosl_version.is_file() and "BOSL_VERSION = [2,0,752]" in bosl_version.read_text()
    results.append(("BOSL2 2.0.752", bosl_ok, str(bosl_version)))
    for executable in ("herdr", "bat"):
        path = shutil.which(executable)
        results.append((executable, path is not None, path or "not found on PATH"))
    herdr_snapshot = run(["herdr", "api", "snapshot"]) if shutil.which("herdr") else None
    results.append(
        (
            "Herdr control plane",
            bool(herdr_snapshot and herdr_snapshot.returncode == 0),
            "" if herdr_snapshot is None else herdr_snapshot.stderr.strip(),
        )
    )

    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="scadctl-doctor-", dir=TMP_ROOT) as temporary:
        temp = Path(temporary)
        source = temp / "doctor.scad"
        source.write_text('include <BOSL2/std.scad>\ncuboid([4, 5, 6], anchor=BOTTOM);\n')
        mesh = temp / "doctor.stl"
        render = run(["openscad", "--backend=Manifold", "--hardwarnings", "-o", str(mesh), str(source)])
        results.append(("Headless BOSL2 mesh export", render.returncode == 0 and mesh.is_file(), render.stderr.strip()))
        image = temp / "doctor.png"
        preview = run(
            [
                "xvfb-run",
                "-a",
                "-s",
                "-screen 0 800x600x24",
                "openscad",
                "--backend=Manifold",
                "--render=true",
                "--autocenter",
                "--viewall",
                "--imgsize=320,240",
                "-o",
                str(image),
                str(source),
            ]
        )
        results.append(("Headless PNG render", preview.returncode == 0 and image.is_file(), preview.stderr.strip()))

    for name, passed, detail in results:
        print(f"{'PASS' if passed else 'FAIL'}  {name}")
        if not passed and detail:
            print(textwrap.indent(detail, "      "))
    return all(passed for _, passed, _ in results)


def load_report(model_dir: Path) -> dict[str, Any]:
    report_path = model_dir / "build/report.json"
    if not report_path.is_file():
        raise UserError(f"No verification report. Run: scadctl verify {model_dir}")
    return json.loads(report_path.read_text())


def review_model(model_dir: Path, inspection_path: Path) -> dict[str, Any]:
    report = load_report(model_dir)
    if not report["technical_pass"]:
        raise UserError("Cannot record visual review while technical checks are failing")
    inspection = json.loads(inspection_path.expanduser().read_text())
    if inspection.get("schema_version") != 2:
        raise UserError("Inspection input must use schema_version 2")
    if inspection.get("artifact_digest") != report.get("artifact_digest"):
        raise UserError("Inspection input is stale or belongs to different artifacts")
    if inspection.get("reviewer", {}).get("kind") != "agent":
        raise UserError("Inspection reviewer.kind must be agent")
    allowed = {"pass", "fail", "uncertain"}
    expected_views = set(PREVIEW_VIEWS)
    view_items = inspection.get("views")
    if not isinstance(view_items, list) or len(view_items) != len(expected_views) or {item.get("id") for item in view_items} != expected_views:
        raise UserError("Inspection must contain exactly the ten generated views")
    for item in view_items:
        if item.get("verdict") not in allowed or not str(item.get("observations", "")).strip():
            raise UserError(f"View {item.get('id')} needs a verdict and observations")
    expected_requirements = {
        item["id"]: set(item["views"])
        for item in report.get("requirements", []) if item["method"] == "visual"
    }
    requirement_items = inspection.get("requirements")
    if not isinstance(requirement_items, list) or len(requirement_items) != len(expected_requirements) or {item.get("id") for item in requirement_items} != set(expected_requirements):
        raise UserError("Inspection visual requirements do not match the current manifest")
    for item in requirement_items:
        evidence = item.get("evidence_views")
        confidence = item.get("confidence")
        if item.get("verdict") not in allowed or not str(item.get("observations", "")).strip():
            raise UserError(f"Visual requirement {item.get('id')} needs a verdict and observations")
        if not isinstance(evidence, list) or not evidence or not set(evidence) <= expected_views:
            raise UserError(f"Visual requirement {item.get('id')} has invalid evidence views")
        if not set(evidence) <= expected_requirements[item["id"]]:
            raise UserError(f"Visual requirement {item.get('id')} cites an undeclared view")
        if isinstance(confidence, bool) or not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
            raise UserError(f"Visual requirement {item.get('id')} confidence must be between 0 and 1")
    verdicts = [item["verdict"] for item in [*view_items, *requirement_items]]
    status = "fail" if "fail" in verdicts else "uncertain" if "uncertain" in verdicts else "pass"
    review = {**inspection, "status": status, "reviewed_at": utc_now()}
    review_path = model_dir / "build/review.json"
    review_path.write_text(json.dumps(review, indent=2, sort_keys=True) + "\n")
    report["visual_review"] = review
    (model_dir / "build/report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    (model_dir / "build/report.md").write_text(report_markdown(report))
    return review


def herdr_json(arguments: Sequence[str], *, check: bool = True) -> dict[str, Any]:
    result = run(["herdr", *arguments])
    if result.returncode:
        if check:
            raise UserError(f"herdr {' '.join(arguments)} failed: {result.stderr.strip()}")
        return {}
    if not result.stdout.strip():
        return {}
    payload = json.loads(result.stdout)
    return payload.get("result", payload)


def herdr_socket_request(method: str, params: dict[str, Any]) -> dict[str, Any]:
    socket_value = os.environ.get("HERDR_SOCKET_PATH")
    if not socket_value:
        raise UserError("Native preview requires running scadctl inside the target Herdr session")
    socket_path = Path(socket_value)
    if not socket_path.exists():
        raise UserError(f"Herdr socket does not exist: {socket_path}")
    request_id = f"scadctl-{uuid.uuid4().hex}"
    request = json.dumps({"id": request_id, "method": method, "params": params}, separators=(",", ":")) + "\n"
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
        connection.settimeout(10)
        connection.connect(str(socket_path))
        connection.sendall(request.encode())
        response = b""
        while b"\n" not in response:
            chunk = connection.recv(1024 * 1024)
            if not chunk:
                break
            response += chunk
    if not response:
        raise UserError(f"Herdr returned no response for {method}")
    payload = json.loads(response.splitlines()[0])
    if "error" in payload:
        error = payload["error"]
        message = error.get("message", error.get("code", "unknown error"))
        if error.get("code") == "cell_size_unavailable":
            raise UserError(
                "Native Herdr graphics are enabled, but the attached outer terminal did not report pixel cell size. "
                "Reattach Herdr from Ghostty, Kitty, or WezTerm, then retry."
            )
        raise UserError(f"Herdr {method} failed: {message}")
    return payload.get("result", payload)


def pane_grid_size(pane_id: str) -> tuple[int, int]:
    result = herdr_json(["pane", "layout", "--pane", pane_id])
    layout = result.get("layout", result)
    pane = next((item for item in layout.get("panes", []) if item.get("pane_id") == pane_id), None)
    rect = (pane or {}).get("rect")
    if not rect:
        raise UserError(f"Herdr snapshot has no layout geometry for pane {pane_id}")
    cols = int(rect.get("width", 0))
    rows = int(rect.get("height", 0))
    if cols <= 0 or rows <= 0:
        raise UserError(f"Herdr snapshot has no viewport size for pane {pane_id}")
    return cols, rows


def aspect_fit_placement(
    image_size: tuple[int, int], grid_size: tuple[int, int], cell_size: tuple[int, int]
) -> dict[str, int]:
    image_width, image_height = image_size
    max_cols, max_rows = grid_size
    cell_width, cell_height = cell_size
    if min(image_width, image_height, max_cols, max_rows, cell_width, cell_height) <= 0:
        raise UserError("Native preview dimensions must be positive")
    image_aspect = image_width / image_height
    available_aspect = (max_cols * cell_width) / (max_rows * cell_height)
    if image_aspect >= available_aspect:
        cols = max_cols
        rows = max(1, min(max_rows, round((cols * cell_width / image_aspect) / cell_height)))
    else:
        rows = max_rows
        cols = max(1, min(max_cols, round((rows * cell_height * image_aspect) / cell_width)))
    return {
        "viewport_col": (max_cols - cols) // 2,
        "viewport_row": (max_rows - rows) // 2,
        "grid_cols": cols,
        "grid_rows": rows,
    }


def set_native_preview(pane_id: str, image_path: Path) -> dict[str, Any]:
    info = herdr_socket_request("pane.graphics.info", {"pane_id": pane_id})
    if not info.get("cell_width_px") or not info.get("cell_height_px"):
        raise UserError("Herdr native graphics did not report a usable pixel cell size")
    cols, rows = pane_grid_size(pane_id)
    with Image.open(image_path) as image:
        width, height = image.size
    placement = aspect_fit_placement(
        (width, height),
        (cols, rows),
        (int(info["cell_width_px"]), int(info["cell_height_px"])),
    )
    result = herdr_socket_request(
        "pane.graphics.set",
        {
            "pane_id": pane_id,
            "format": "png",
            "image_width": width,
            "image_height": height,
            "data_base64": base64.b64encode(image_path.read_bytes()).decode("ascii"),
            "placement": placement,
        },
    )
    return {
        "mode": "native-herdr",
        "source": image_path.name,
        "image_size_px": [width, height],
        "cell_size_px": [info["cell_width_px"], info["cell_height_px"]],
        "grid_size": [cols, rows],
        "placement": placement,
        "result": result,
    }


def nested_value(value: Any, keys: set[str]) -> str | None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key in keys and isinstance(item, str):
                return item
        for item in value.values():
            found = nested_value(item, keys)
            if found:
                return found
    elif isinstance(value, list):
        for item in value:
            found = nested_value(item, keys)
            if found:
                return found
    return None


def record_id(record: dict[str, Any], kind: str) -> str | None:
    return record.get(f"{kind}_id") or record.get("id")


def records(result: dict[str, Any], kind: str) -> list[dict[str, Any]]:
    items = result.get(f"{kind}s", [])
    return [item for item in items if isinstance(item, dict)]


def pane_for_tab(workspace_id: str, tab_id: str) -> str:
    panes = records(herdr_json(["pane", "list", "--workspace", workspace_id]), "pane")
    candidates = [pane for pane in panes if pane.get("tab_id") == tab_id]
    primary = [pane for pane in candidates if not pane.get("label")]
    selected = primary[0] if len(primary) == 1 else candidates[0] if len(candidates) == 1 else None
    pane_id = record_id(selected, "pane") if selected else None
    if not pane_id:
        raise UserError(f"Herdr did not report one unambiguous primary pane for tab {tab_id}")
    return pane_id


def create_tab(workspace_id: str, model_dir: Path, label: str) -> dict[str, str]:
    created = herdr_json(
        ["tab", "create", "--workspace", workspace_id, "--cwd", str(model_dir), "--label", label, "--no-focus"]
    )
    tab_id = nested_value(created, {"tab_id"})
    if not tab_id:
        raise UserError(f"Herdr did not return an ID for the {label} tab")
    return {"tab_id": tab_id, "pane_id": pane_for_tab(workspace_id, tab_id)}


def zoom_primary_panes(tabs: dict[str, dict[str, str]]) -> None:
    """Give generated presentation panes the full tab while preserving managed side panes."""
    result = herdr_json(["api", "snapshot"])
    snapshot = result.get("snapshot", result)
    layouts = {item.get("tab_id"): item for item in snapshot.get("layouts", [])}
    for tab in tabs.values():
        layout = layouts.get(tab["tab_id"], {})
        if len(layout.get("panes", [])) > 1 and (
            not layout.get("zoomed") or layout.get("focused_pane_id") != tab["pane_id"]
        ):
            herdr_json(["pane", "zoom", tab["pane_id"]])


def prepare_workspace(model_dir: Path, label: str, prior: dict[str, Any]) -> tuple[str, dict[str, dict[str, str]]]:
    workspace_id = prior.get("workspace_id")
    if workspace_id and not herdr_json(["workspace", "get", workspace_id], check=False):
        workspace_id = None
    if not workspace_id:
        matches = [
            item for item in records(herdr_json(["workspace", "list"]), "workspace")
            if item.get("label") == label
        ]
        if len(matches) > 1:
            raise UserError(f"More than one Herdr workspace is labeled {label!r}; resolve the duplicate first")
        workspace_id = record_id(matches[0], "workspace") if matches else None
    tabs: dict[str, dict[str, str]] = {}
    if not workspace_id:
        created = herdr_json(["workspace", "create", "--cwd", str(model_dir), "--label", label, "--no-focus"])
        workspace_id = nested_value(created, {"workspace_id"})
        if not workspace_id:
            raise UserError("Herdr did not return a workspace ID")
        existing_tabs = records(herdr_json(["tab", "list", "--workspace", workspace_id]), "tab")
        if len(existing_tabs) != 1:
            raise UserError("A new Herdr workspace did not contain exactly one initial tab")
        preview_id = record_id(existing_tabs[0], "tab")
        if not preview_id:
            raise UserError("Herdr did not return the initial tab ID")
        herdr_json(["tab", "rename", preview_id, "Isometric Front"])
        tabs["Isometric Front"] = {"tab_id": preview_id, "pane_id": pane_for_tab(workspace_id, preview_id)}
    current_tabs = records(herdr_json(["tab", "list", "--workspace", workspace_id]), "tab")
    legacy_preview = next((item for item in current_tabs if item.get("label") == "Preview"), None)
    has_isometric_front = any(item.get("label") == "Isometric Front" for item in current_tabs)
    if legacy_preview and not has_isometric_front:
        legacy_id = record_id(legacy_preview, "tab")
        if not legacy_id:
            raise UserError("Herdr did not report an ID for the legacy Preview tab")
        herdr_json(["tab", "rename", legacy_id, "Isometric Front"])
        legacy_preview["label"] = "Isometric Front"
    by_id = {record_id(item, "tab"): item for item in current_tabs}
    by_label = {item.get("label"): item for item in current_tabs}
    for tab_label in PRESENTATION_TABS:
        saved = prior.get("tabs", {}).get(tab_label, {})
        candidate = by_id.get(saved.get("tab_id")) or by_label.get(tab_label)
        if candidate and record_id(candidate, "tab"):
            tab_id = record_id(candidate, "tab")
            tabs[tab_label] = {"tab_id": tab_id, "pane_id": pane_for_tab(workspace_id, tab_id)}
        elif tab_label not in tabs:
            tabs[tab_label] = create_tab(workspace_id, model_dir, tab_label)
    return workspace_id, tabs


def populate_pane(pane_id: str, command: str, timeout: float = 15.0) -> None:
    token = uuid.uuid4().hex
    marker = f"SCADCTL_PRESENT_READY:{token}:"
    wrapped = f"{command}; present_rc=$?; printf '\\n{marker}%s\\n' \"$present_rc\""
    herdr_json(["pane", "run", pane_id, wrapped])
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        recent = run(["herdr", "pane", "read", pane_id, "--source", "recent-unwrapped", "--lines", "40", "--format", "text"])
        visible = run(["herdr", "pane", "read", pane_id, "--source", "visible", "--format", "text"])
        match = re.search(re.escape(marker) + r"(\d+)", recent.stdout + "\n" + visible.stdout)
        if match:
            if int(match.group(1)):
                raise UserError(f"Presentation command failed in pane {pane_id} with exit {match.group(1)}")
            return
        time.sleep(0.1)
    raise UserError(f"Timed out waiting for presentation pane {pane_id}")


def present_model(model_dir: Path, *, focus: bool = True) -> dict[str, Any]:
    report = load_report(model_dir)
    if not report.get("technical_pass"):
        raise UserError("Cannot present while technical checks are failing")
    review = report.get("visual_review", {})
    if review.get("status") != "pass" or review.get("artifact_digest") != report.get("artifact_digest"):
        raise UserError("Current artifacts need a passing agent visual review before presentation")
    build_dir = model_dir / "build"
    state_path = build_dir / "presentation.json"
    prior = json.loads(state_path.read_text()) if state_path.is_file() else {}
    workspace_state = records(herdr_json(["workspace", "list"]), "workspace")
    previously_focused = next((item for item in workspace_state if item.get("focused")), None)
    label = f"OpenSCAD · {report['model']}"
    workspace_id, tabs = prepare_workspace(model_dir, label, prior)
    for index, tab_label in enumerate(PRESENTATION_TABS):
        herdr_socket_request("tab.move", {"tab_id": tabs[tab_label]["tab_id"], "insert_index": index})
    commands = {
        **{
            label: f"clear; printf 'Native Herdr image preview: {view}.png\\n'"
            for view, label in PRESENTATION_VIEW_LABELS.items()
        },
        "Spec": f"clear; bat --paging=never --style=header,grid {shlex.quote(str(model_dir / 'spec.md'))}",
        "Report": f"clear; bat --paging=never --style=header,grid {shlex.quote(str(build_dir / 'report.md'))}",
        "Source": f"clear; bat --paging=never --style=header,grid,numbers {shlex.quote(str(model_dir / 'model.scad'))}",
    }
    for tab_label in (*PRESENTATION_VIEW_LABELS.values(), "Spec", "Source"):
        populate_pane(tabs[tab_label]["pane_id"], commands[tab_label])
    presentation = {
        "schema_version": 2,
        "status": "presented",
        "preview_mode": "native-herdr",
        "artifact_digest": report["artifact_digest"],
        "workspace_id": workspace_id,
        "workspace_label": label,
        "tabs": tabs,
        "presented_at": utc_now(),
    }
    report["presentation"] = presentation
    (build_dir / "report.md").write_text(report_markdown(report))
    populate_pane(tabs["Report"]["pane_id"], commands["Report"])
    zoom_primary_panes(tabs)
    if focus:
        herdr_json(["workspace", "focus", workspace_id])
        herdr_json(["tab", "focus", tabs["Isometric Front"]["tab_id"]])
    elif previously_focused:
        prior_workspace_id = record_id(previously_focused, "workspace")
        if prior_workspace_id:
            herdr_json(["workspace", "focus", prior_workspace_id])
        if previously_focused.get("active_tab_id"):
            herdr_json(["tab", "focus", previously_focused["active_tab_id"]])
    presentation["native_previews"] = {
        label: set_native_preview(tabs[label]["pane_id"], build_dir / "previews" / f"{view}.png")
        for view, label in PRESENTATION_VIEW_LABELS.items()
    }
    report["presentation"] = presentation
    state_path.write_text(json.dumps(presentation, indent=2, sort_keys=True) + "\n")
    (build_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return presentation


def final_status(model_dir: Path) -> bool:
    report = load_report(model_dir)
    review_path = model_dir / "build/review.json"
    review = json.loads(review_path.read_text()) if review_path.is_file() else {}
    review_current = review.get("artifact_digest") == report.get("artifact_digest")
    visual_pass = review_current and review.get("status") == "pass"
    visual_display = "PASS" if visual_pass else review.get("status", "PENDING").upper()
    if review and not review_current:
        visual_display = "STALE"
    presentation = presentation_for_digest(model_dir / "build", report.get("artifact_digest"))
    presented = presentation.get("status") == "presented"
    print(f"Technical: {'PASS' if report['technical_pass'] else 'FAIL'}")
    print(f"Visual:    {visual_display}")
    print(f"Presented: {'PASS' if presented else presentation.get('status', 'missing').upper()}")
    overall = bool(report["technical_pass"] and visual_pass and presented)
    print(f"Overall:   {'PASS' if overall else 'FAIL'}")
    return overall


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="scadctl", description="Build and verify single-solid OpenSCAD models")
    root.add_argument("--version", action="version", version=f"scadctl {__version__}")
    commands = root.add_subparsers(dest="command", required=True)
    commands.add_parser("doctor", help="check the installed CAD toolchain")
    new = commands.add_parser("new", help="create a model scaffold")
    new.add_argument("name")
    verify = commands.add_parser("verify", help="export, validate, and render a model")
    verify.add_argument("model")
    review = commands.add_parser("review", help="record a structured visual inspection of current artifacts")
    review.add_argument("model")
    review.add_argument("--input", required=True, type=Path, help="completed schema-v2 inspection JSON")
    present = commands.add_parser("present", help="show verified artifacts in a dedicated Herdr workspace")
    present.add_argument("model")
    present.add_argument("--no-focus", action="store_true", help="refresh without focusing the Preview tab")
    status = commands.add_parser("status", help="check technical, visual, and presentation approval")
    status.add_argument("model")
    return root


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "doctor":
            return 0 if doctor() else 1
        if args.command == "new":
            created = scaffold(args.name)
            print(created)
            return 0
        model_dir = resolve_model(args.model)
        if args.command == "verify":
            report = verify_model(model_dir)
            print(f"Technical: {'PASS' if report['technical_pass'] else 'FAIL'}")
            print(f"Visual:    {report['visual_review']['status'].upper()}")
            print(model_dir / "build/report.md")
            return 0 if report["technical_pass"] else 1
        if args.command == "review":
            review = review_model(model_dir, args.input)
            print(f"Recorded visual review: {review['status'].upper()}")
            return 0
        if args.command == "present":
            presentation = present_model(model_dir, focus=not args.no_focus)
            print(f"Presented in Herdr workspace {presentation['workspace_id']}")
            return 0
        if args.command == "status":
            return 0 if final_status(model_dir) else 1
    except (UserError, OSError, ValueError, tomllib.TOMLDecodeError, json.JSONDecodeError) as error:
        print(f"scadctl: {error}", file=sys.stderr)
        return 2
    return 2
