# Contributing

Thanks for helping improve OpenSCAD Workbench.

## Development setup

The supported development environment is Linux on x86-64 with Python 3.13,
`curl`, `dpkg-deb`, `tar`, `zsh`, Xvfb, and ShellCheck available. Bootstrap the
pinned OpenSCAD, BOSL2, and Python dependencies in user space:

```sh
git clone https://github.com/geraldsummers/openscad-workbench.git
cd openscad-workbench
scripts/bootstrap
scripts/check
```

The bootstrap installs launchers in `$HOME/.local/bin`. Ensure that directory
is on `PATH` before running `scadctl`.

## Making changes

- Keep models as one connected solid and grounded at Z=0.
- Add stable requirement IDs to both `spec.md` and the schema-v2 `model.toml`.
- Add or update tests for verifier and presentation behavior.
- Run the narrowest relevant tests while iterating, then run `scripts/check`.
- Do not commit `.venv`, model build directories, exported meshes, or preview
  images.

Pull requests should explain the user-visible behavior, validation performed,
and any requirement that still depends on physical measurement or testing.

The complete local check includes `scadctl doctor` and therefore expects Herdr
and `bat`. CI uses `scripts/check --no-doctor` because it validates the portable
CLI and render toolchain without a persistent Herdr session.

## Reporting problems

Use the GitHub issue forms for reproducible bugs and feature proposals. Please
use GitHub's private vulnerability reporting instead of public issues for
security-sensitive findings.
