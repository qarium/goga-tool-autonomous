# goga as a dependency — how this package connects the platform

Domain: declaring (and not declaring) the goga platform as a dependency of the
`goga-tool-autonomous` package. Audience: maintainers of the package and contributors updating
the dependency manifest.

## The rule

- **Runtime: never declare goga.** The package's runtime dependencies stay empty. A goga tool is
  installed into a goga-provided interpreter (the project's goga image) — the ecosystem provides
  goga, and declaring it again risks resolver conflicts inside that image.
- **Import safety without a declaration.** Importing platform modules inside the package (for
  example the workflow model from `goga.pipeline.workflow`) is safe because goga itself imports
  the package facade — the platform is present in the interpreter whenever the package runs.
- **Tests: declare goga unpinned.** The test extra declares `goga>=2.0` with no upper bound, so a
  future platform release that changes the development-pipeline shape surfaces as test failures
  instead of silently passing or stalling unattended runs.

## Manifest shape

```toml
[project]
dependencies = []          # runtime — stays empty

[project.optional-dependencies]
test = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "pytest-mock>=3.10",
    "ruff>=0.15.0",
    "goga>=2.0",           # test-only, no upper bound
]
```

## What this means in practice

- Never add goga to the runtime dependencies — not even with a lower bound.
- Keep the test-extra entry unpinned above (`>=2.0`, no upper bound).
- Installing the package into a plain (non-goga) environment is out of scope: the package only
  runs inside a goga-provided interpreter.
