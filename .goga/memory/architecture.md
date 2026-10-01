# Project rules

## Pipeline-explicit naming

Identifiers for pipeline-specific functionality must state the pipeline they serve in the name itself; generic names that hide the target pipeline are rejected.

## Zone sub-cell decomposition with facade re-export

Each knowledge zone is split into per-pipeline sub-cells from the start, and the zone's API is re-exported from the main cell facade via embeddings. Adding a pipeline later means one new sub-cell plus a registry entry and an embedding — never new type declarations on the facade.

## Upward-only dependency layering

Cell dependencies form a linear leaves-to-root chain: sub-cells, then the parent zone cell, then the main cell. No cell imports from its ancestor; when sharing would demand a downward edge, the shared shape is extracted into a leaf sub-cell so every edge points up.

## Functional-domain partitioning of usage documentation

Facade usage documentation is partitioned by functional domain, where one domain equals one pipeline zone — never by action kind — and the partition is established immediately, even while only a single domain exists, so the architecture scales by addition rather than restructuring.

## Leveled ownership of usage files

Usage documentation follows a three-level scheme: the main cell's facade documents the tool level for potential consumers; the parent zone cell serves domain-level usage files from its own facade; sub-cells keep usage files only for interactions wired inside their parent cell.

## Contract-only global annotations

A cell's global annotation holds statements about the contract itself only; the arrangement of usage files and pipeline-to-documentation mappings belong to the documentation level and the architecture plan, not to the annotation.

## Single-source consumption of external specifications

External platform surfaces are consumed by referencing the existing synced read-only dependency specifications by path; restating such a surface in a new project usage file is rejected as ignoring the dependency specs.

## Required dependency-connection documentation

The knowledge for connecting the host platform as a dependency must exist as an explicit spec in the project's operational documentation, be wired into the main cell's usage header, and have its requirement stated in the main cell's global annotation — it is never left implicit.

## Pure hook with import-clean facade

The entry hook is a pure function of its delivered input: it gates on the exact pipeline identity, stays silent for unmatched pipelines, keeps no state or cache, and performs no internal exception handling, so failures propagate outward as clean errors; the package facade must remain importable unconditionally, because an import failure is fatal to every command of the host platform.

## Platform-owned behavior boundary

Behaviors owned by the host platform — merge semantics, compilation, and validation of contributed content — are never re-implemented in the tool; the tool contributes only declarative content and asserts expected outcomes with tests run against the platform's real functions.
