# Project rules

## Fixture path resolution

Shared test fixtures pointing at project-root artifacts must compute the path with explicit resolution (for symlink robustness) and a parent-index that matches the fixture file's real depth below the root; the computed path is confirmed to resolve to the actual file before the fixture is trusted.

## Edge-condition test pinning

Every boundary behavior declared in a design must be secured either by a complete test trace (setup, input, execution, assertions, sufficiency) or by an explicit recorded coverage gap; behavior that exists only in prose counts as a review finding.

## Authored-content precedence

A tool contributing amendments to an authored artifact must remain neutral toward it: entries already present in the authored artifact always win over contributed ones, and a contribution equal to the authored state must produce output byte-identical to the authored reference.

## Minimal-contribution guarantee

A delivery's contributed document must never be empty: an unconditional core is always contributed even when every optional input list is empty, because the consuming platform silently discards empty contributions.

## Document-internal consistency

Every step of a declared test or execution trace must reference the entities its own setup actually creates; mentions left over from earlier draft editions are corrected to match the real setup so implementers are not misdirected.
