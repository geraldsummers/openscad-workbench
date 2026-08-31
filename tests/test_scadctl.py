from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image
import trimesh

from scadctl import cli


def test_valid_box_metrics_pass_fixed_geometry_gate() -> None:
    mesh = trimesh.creation.box(extents=[40, 30, 12])
    mesh.apply_translation([0, 0, 6])
    metrics = cli.mesh_metrics(mesh)
    checks: list[cli.Check] = []

    cli.add_mesh_checks(checks, "stl", metrics, cli.DEFAULT_ENVELOPE, cli.DEFAULT_TOLERANCE)

    assert all(check.passed for check in checks)
    assert metrics["body_count"] == 1
    assert metrics["manifold_status"] == "Error.NoError"


def test_disconnected_bodies_fail_one_body_check() -> None:
    first = trimesh.creation.box()
    second = trimesh.creation.box()
    second.apply_translation([3, 0, 0])
    mesh = trimesh.util.concatenate([first, second])
    mesh.apply_translation([0, 0, 0.5])
    metrics = cli.mesh_metrics(mesh)
    checks: list[cli.Check] = []

    cli.add_mesh_checks(checks, "stl", metrics, cli.DEFAULT_ENVELOPE, cli.DEFAULT_TOLERANCE)

    one_body = next(check for check in checks if check.name == "stl.one_body")
    assert not one_body.passed
    assert one_body.actual == 2


def test_oversize_and_wrong_z_fail() -> None:
    mesh = trimesh.creation.box(extents=[271, 20, 10])
    mesh.apply_translation([0, 0, 6])
    metrics = cli.mesh_metrics(mesh)
    checks: list[cli.Check] = []

    cli.add_mesh_checks(checks, "stl", metrics, cli.DEFAULT_ENVELOPE, cli.DEFAULT_TOLERANCE)

    by_name = {check.name: check for check in checks}
    assert not by_name["stl.build_envelope"].passed
    assert not by_name["stl.touches_z0"].passed


def test_stl_and_3mf_comparison_detects_changed_bounds() -> None:
    stl = {"bounds_mm": [[0, 0, 0], [10, 10, 10]], "volume_mm3": 1000.0}
    three_mf = {"bounds_mm": [[0, 0, 0], [11, 10, 10]], "volume_mm3": 1100.0}
    checks: list[cli.Check] = []

    cli.compare_meshes(checks, stl, three_mf, 0.01)

    assert not any(check.passed for check in checks)


def test_review_is_bound_to_current_artifact_digest(tmp_path: Path) -> None:
    build = tmp_path / "build"
    build.mkdir()
    report = {
        "model": "fixture",
        "technical_pass": True,
        "artifact_digest": "current",
        "visual_review": {"schema_version": 2, "status": "pending", "artifact_digest": None},
        "requirements": [{"id": "shape", "method": "visual", "views": list(cli.PREVIEW_VIEWS)}],
        "checks": [],
    }
    (build / "report.json").write_text(json.dumps(report))
    inspection = cli.inspection_template(report["requirements"], "current")
    for item in inspection["views"]:
        item.update(verdict="pass", observations="View is complete and unclipped")
    inspection["requirements"][0].update(
        verdict="pass", observations="All views show the intended solid", confidence=0.99
    )
    inspection_path = tmp_path / "inspection.json"
    inspection_path.write_text(json.dumps(inspection))

    cli.review_model(tmp_path, inspection_path)
    (build / "presentation.json").write_text(
        json.dumps({"status": "presented", "artifact_digest": "current", "preview_mode": "native-herdr", "native_previews": {label: {"cell_size_px": [8, 16]} for label in cli.PRESENTATION_VIEW_LABELS.values()}})
    )
    assert cli.final_status(tmp_path)

    report["artifact_digest"] = "changed"
    (build / "report.json").write_text(json.dumps(report))
    assert not cli.final_status(tmp_path)


def test_status_requires_current_presentation(tmp_path: Path) -> None:
    build = tmp_path / "build"
    build.mkdir()
    report = {
        "model": "fixture",
        "technical_pass": True,
        "artifact_digest": "current",
        "visual_review": {"status": "pass", "artifact_digest": "current"},
        "checks": [],
    }
    (build / "report.json").write_text(json.dumps(report))
    (build / "review.json").write_text(json.dumps(report["visual_review"]))

    assert not cli.final_status(tmp_path)
    (build / "presentation.json").write_text(json.dumps({"artifact_digest": "old"}))
    assert not cli.final_status(tmp_path)
    (build / "presentation.json").write_text(json.dumps({"artifact_digest": "current", "preview_mode": "native-herdr", "native_previews": {label: {"cell_size_px": [8, 16]} for label in cli.PRESENTATION_VIEW_LABELS.values()}}))
    assert cli.final_status(tmp_path)


def test_present_populates_all_tabs_then_focuses_preview(tmp_path: Path, monkeypatch) -> None:
    build = tmp_path / "build"
    previews = build / "previews"
    previews.mkdir(parents=True)
    for name in cli.PREVIEW_VIEWS:
        (previews / f"{name}.png").write_bytes(b"png")
    (tmp_path / "spec.md").write_text("spec")
    (tmp_path / "model.scad").write_text("cube(1);")
    report = {
        "model": "fixture",
        "technical_pass": True,
        "artifact_digest": "digest",
        "visual_review": {"status": "pass", "artifact_digest": "digest"},
        "checks": [],
    }
    (build / "report.json").write_text(json.dumps(report))
    (build / "report.md").write_text("report")
    tabs = {name: {"tab_id": f"t-{name}", "pane_id": f"p-{name}"} for name in cli.PRESENTATION_TABS}
    calls: list[tuple] = []
    monkeypatch.setattr(cli, "prepare_workspace", lambda *_: ("w-model", tabs))
    monkeypatch.setattr(cli, "populate_pane", lambda pane, command: calls.append(("populate", pane, command)))
    monkeypatch.setattr(cli, "herdr_socket_request", lambda method, params: {"cell_width_px": 8, "cell_height_px": 16})
    monkeypatch.setattr(cli, "set_native_preview", lambda pane, path: {"mode": "native-herdr", "source": path.name})
    monkeypatch.setattr(
        cli,
        "herdr_json",
        lambda args, **_: calls.append(tuple(args)) or ({"workspaces": []} if args == ["workspace", "list"] else {}),
    )

    presentation = cli.present_model(tmp_path)

    populate_calls = [call for call in calls if call[0] == "populate"]
    assert [call[1] for call in populate_calls] == [
        *[f"p-{label}" for label in cli.PRESENTATION_VIEW_LABELS.values()], "p-Spec", "p-Source", "p-Report"
    ]
    assert "isometric-front.png" in populate_calls[0][2]
    assert calls[-2:] == [("workspace", "focus", "w-model"), ("tab", "focus", "t-Isometric Front")]
    assert presentation["workspace_id"] == "w-model"
    assert presentation["preview_mode"] == "native-herdr"
    assert set(presentation["native_previews"]) == set(cli.PRESENTATION_VIEW_LABELS.values())
    assert json.loads((build / "presentation.json").read_text())["artifact_digest"] == "digest"


def test_expected_extents_are_exact_with_tolerance() -> None:
    checks: list[cli.Check] = []
    metrics = {"extents_mm": np.array([40.005, 29.995, 12.0]).tolist()}
    geometry = {"expected_extents_mm": [40, 30, 12], "expected_extents_tolerance_mm": 0.01}

    cli.check_expected_extents(checks, metrics, geometry)

    assert checks[0].passed


def test_open_mesh_fails_watertight_and_manifold_checks() -> None:
    mesh = trimesh.creation.box()
    mesh.update_faces(np.arange(len(mesh.faces)) != 0)
    metrics = cli.mesh_metrics(mesh)
    checks: list[cli.Check] = []

    cli.add_mesh_checks(checks, "stl", metrics, cli.DEFAULT_ENVELOPE, cli.DEFAULT_TOLERANCE)

    by_name = {check.name: check for check in checks}
    assert not by_name["stl.watertight"].passed
    assert not by_name["stl.manifold3d"].passed


def test_inverted_mesh_fails_positive_volume() -> None:
    mesh = trimesh.creation.box()
    mesh.faces = np.fliplr(mesh.faces)
    mesh.apply_translation([0, 0, 0.5])
    metrics = cli.mesh_metrics(mesh)
    checks: list[cli.Check] = []

    cli.add_mesh_checks(checks, "stl", metrics, cli.DEFAULT_ENVELOPE, cli.DEFAULT_TOLERANCE)

    positive_volume = next(check for check in checks if check.name == "stl.positive_volume")
    assert not positive_volume.passed


def test_degenerate_and_duplicate_faces_are_reported() -> None:
    mesh = trimesh.creation.box()
    mesh.faces = np.vstack([mesh.faces, mesh.faces[0], [0, 0, 1]])
    metrics = cli.mesh_metrics(mesh)

    assert not metrics["all_faces_unique"]
    assert not metrics["all_faces_nondegenerate"]


def test_openscad_parser_error_fails_clean_export(tmp_path: Path) -> None:
    source = tmp_path / "broken.scad"
    source.write_text("cube([1, 2, 3]); this is not valid;\n")

    result, artifacts = cli.export_geometry(source, tmp_path)

    assert result.returncode != 0 or cli.FAILURE_PATTERN.search(result.stdout + result.stderr)
    assert not all(path.is_file() and path.stat().st_size for path in artifacts)


def test_openscad_hardwarning_fails_clean_export(tmp_path: Path) -> None:
    source = tmp_path / "warning.scad"
    source.write_text("cube([missing_dimension, 2, 3]);\n")

    result, _ = cli.export_geometry(source, tmp_path)

    assert result.returncode != 0 or cli.FAILURE_PATTERN.search(result.stdout + result.stderr)


def test_scaffold_creates_contract_files(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(cli, "MODELS", tmp_path)

    model = cli.scaffold("sample-part")

    assert (model / "model.scad").is_file()
    assert (model / "model.toml").is_file()
    assert (model / "spec.md").is_file()
    config = cli.read_config(model)
    assert config["geometry"]["connected_components"] == 1


def test_geometry_digest_ignores_face_order() -> None:
    first = trimesh.creation.box()
    second = first.copy()
    second.faces = second.faces[::-1]

    assert cli.mesh_geometry_digest(first) == cli.mesh_geometry_digest(second)


def test_mesh_metrics_include_explicit_topology() -> None:
    metrics = cli.mesh_metrics(trimesh.creation.box())

    assert metrics["boundary_edges"] == 0
    assert metrics["nonmanifold_edges"] == 0
    assert metrics["isolated_vertices"] == 0
    assert metrics["euler_number"] == 2
    assert metrics["genus"] == 0


def test_global_region_symmetry_and_section_requirements() -> None:
    mesh = trimesh.creation.box(extents=[10, 8, 6])
    requirements = [
        {"id": "size", "method": "mesh", "kind": "extents", "expected": [10, 8, 6], "tolerance": 0.001},
        {"id": "symmetry", "method": "mesh", "kind": "symmetry", "axis": "x", "offset": 0, "max_difference_ratio": 1e-6},
        {"id": "solid-core", "method": "mesh", "kind": "region", "shape": "box", "center": [0, 0, 0], "size": [2, 2, 2], "expected": "solid", "min_fraction": 0.999},
        {"id": "section", "method": "mesh", "kind": "section", "axis": "z", "offset": 0, "expected": {"components": 1, "area_mm2": 80, "bounds_mm": [[-5, -4], [5, 4]]}, "tolerance": 0.001},
    ]

    checks = cli.evaluate_requirements(requirements, mesh, cli.mesh_metrics(mesh), "")

    assert all(check.passed for check in checks)


def test_source_requirement_needs_pass_marker() -> None:
    mesh = trimesh.creation.box()
    requirement = [{"id": "constraint", "method": "source"}]

    assert not cli.evaluate_requirements(requirement, mesh, cli.mesh_metrics(mesh), "")[0].passed
    assert cli.evaluate_requirements(requirement, mesh, cli.mesh_metrics(mesh), "SCADCTL_REQUIREMENT:constraint:PASS")[0].passed


def test_uncertain_structured_review_is_not_a_pass(tmp_path: Path) -> None:
    build = tmp_path / "build"
    build.mkdir()
    requirements = [{"id": "shape", "method": "visual", "views": ["front"]}]
    report = {"technical_pass": True, "artifact_digest": "digest", "requirements": requirements, "checks": [], "model": "fixture"}
    (build / "report.json").write_text(json.dumps(report))
    inspection = cli.inspection_template(requirements, "digest")
    for item in inspection["views"]:
        item.update(verdict="pass", observations="Rendered content is visible")
    inspection["requirements"][0].update(verdict="uncertain", observations="Feature is occluded", confidence=0.4)
    path = tmp_path / "inspection.json"
    path.write_text(json.dumps(inspection))

    review = cli.review_model(tmp_path, path)

    assert review["status"] == "uncertain"
    assert not cli.final_status(tmp_path)


def test_schema_v1_manifest_has_actionable_migration_error(tmp_path: Path) -> None:
    (tmp_path / "model.scad").write_text("cube(1);")
    (tmp_path / "spec.md").write_text("- [shape] Shape")
    (tmp_path / "model.toml").write_text('name="old"\nsource="model.scad"\nunits="mm"\n')

    try:
        cli.read_config(tmp_path)
    except cli.UserError as error:
        assert "schema_version = 2" in str(error)
    else:
        raise AssertionError("schema-v1 manifest was accepted")


def test_spec_requirement_must_have_manifest_mapping(tmp_path: Path) -> None:
    (tmp_path / "model.scad").write_text("cube(1);")
    (tmp_path / "spec.md").write_text("- [shape] Shape\n- [missing] Missing mapping\n")
    (tmp_path / "model.toml").write_text(
        'schema_version=2\nname="part"\nsource="model.scad"\nunits="mm"\n'
        '[[requirements]]\nid="shape"\ndescription="Shape"\nmethod="source"\n'
    )

    try:
        cli.read_config(tmp_path)
    except cli.UserError as error:
        assert "unmapped requirement" in str(error)
    else:
        raise AssertionError("unmapped specification requirement was accepted")


def test_image_sanity_rejects_blank_and_clipped_images(tmp_path: Path) -> None:
    blank = tmp_path / "blank.png"
    Image.new("RGB", (800, 600), "#111827").save(blank)
    clipped = tmp_path / "clipped.png"
    image = Image.new("RGB", (800, 600), "#111827")
    for x in range(100):
        for y in range(100):
            image.putpixel((x, y), (255, 255, 255))
    image.save(clipped)

    blank_metrics = cli.image_metrics(blank)
    clipped_metrics = cli.image_metrics(clipped)

    assert blank_metrics["foreground_fraction"] == 0
    assert clipped_metrics["clipped"]


def test_preview_size_check_requires_full_resolution(tmp_path: Path) -> None:
    preview = tmp_path / "front.png"
    Image.new("RGB", cli.PREVIEW_SIZE, "teal").save(preview)
    checks: list[cli.Check] = []

    cli.add_image_checks(checks, [preview])

    size_check = next(check for check in checks if check.name == "preview.front.size")
    assert size_check.passed
    assert size_check.expected == [1600, 1200]


def test_contact_sheet_uses_manageable_thumbnails(tmp_path: Path) -> None:
    images = []
    for index, name in enumerate(cli.PREVIEW_VIEWS):
        path = tmp_path / f"{name}.png"
        Image.new("RGB", cli.PREVIEW_SIZE, (index * 20, 30, 40)).save(path)
        images.append(path)
    output = tmp_path / "contact-sheet.png"

    cli.create_contact_sheet(images, output)

    with Image.open(output) as sheet:
        assert sheet.size == (3200, 1920)
        assert sheet.getpixel((10, cli.CONTACT_SHEET_TITLE_HEIGHT + 10)) == (0, 30, 40)


def test_review_rejects_stale_inspection(tmp_path: Path) -> None:
    build = tmp_path / "build"
    build.mkdir()
    (build / "report.json").write_text(json.dumps({"technical_pass": True, "artifact_digest": "new", "requirements": []}))
    inspection = cli.inspection_template([], "old")
    path = tmp_path / "inspection.json"
    path.write_text(json.dumps(inspection))

    try:
        cli.review_model(tmp_path, path)
    except cli.UserError as error:
        assert "stale" in str(error)
    else:
        raise AssertionError("stale inspection was accepted")


def test_native_preview_requires_cell_telemetry(tmp_path: Path, monkeypatch) -> None:
    image_path = tmp_path / "preview.png"
    Image.new("RGB", (320, 200), "teal").save(image_path)
    requests: list[tuple[str, dict]] = []

    def request(method: str, params: dict) -> dict:
        requests.append((method, params))
        if method == "pane.graphics.info":
            raise cli.UserError("attached outer terminal did not report pixel cell size")
        return {"type": "ok"}

    monkeypatch.setattr(cli, "herdr_socket_request", request)
    monkeypatch.setattr(cli, "pane_grid_size", lambda _: (100, 40))

    try:
        cli.set_native_preview("w1:p2", image_path)
    except cli.UserError as error:
        assert "pixel cell size" in str(error)
    else:
        raise AssertionError("native preview passed without client cell telemetry")
    assert requests == [("pane.graphics.info", {"pane_id": "w1:p2"})]


def test_native_preview_placement_preserves_pixel_aspect_ratio() -> None:
    placement = cli.aspect_fit_placement(cli.PREVIEW_SIZE, (220, 63), (8, 16))

    assert placement == {"viewport_col": 26, "viewport_row": 0, "grid_cols": 168, "grid_rows": 63}
    displayed_aspect = (placement["grid_cols"] * 8) / (placement["grid_rows"] * 16)
    assert abs(displayed_aspect - (cli.PREVIEW_SIZE[0] / cli.PREVIEW_SIZE[1])) < 0.001


def test_zoom_primary_panes_makes_split_presentation_tabs_full_width(monkeypatch) -> None:
    tabs = {
        "Front": {"tab_id": "t-front", "pane_id": "p-front"},
        "Spec": {"tab_id": "t-spec", "pane_id": "p-spec"},
    }
    layouts = [
        {
            "tab_id": "t-front",
            "focused_pane_id": "p-front",
            "zoomed": False,
            "panes": [{"pane_id": "p-front"}, {"pane_id": "p-front-diff"}],
        },
        {"tab_id": "t-spec", "focused_pane_id": "p-spec", "zoomed": False, "panes": [{"pane_id": "p-spec"}]},
    ]
    zoomed: list[str] = []

    def herdr_json(args: list[str], **_: object) -> dict:
        if args == ["api", "snapshot"]:
            return {"snapshot": {"layouts": layouts}}
        if args[:2] == ["pane", "zoom"]:
            zoomed.append(args[2])
            return {"type": "ok"}
        raise AssertionError(args)

    monkeypatch.setattr(cli, "herdr_json", herdr_json)

    cli.zoom_primary_panes(tabs)

    assert zoomed == ["p-front"]


def test_pane_grid_size_uses_full_area_when_primary_pane_is_zoomed(monkeypatch) -> None:
    snapshot = {
        "panes": [{"pane_id": "p-front", "scroll": {"viewport_rows": 46}}],
        "layouts": [{
            "area": {"width": 238, "height": 48},
            "focused_pane_id": "p-front",
            "zoomed": True,
            "panes": [
                {"pane_id": "p-front", "rect": {"width": 167, "height": 48}},
                {"pane_id": "p-diff", "rect": {"width": 71, "height": 48}},
            ],
        }],
    }
    monkeypatch.setattr(cli, "herdr_json", lambda *_: {"snapshot": snapshot})

    assert cli.pane_grid_size("p-front") == (236, 46)
