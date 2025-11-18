# API Architectural Assessment — Event Operations API

## Executive Summary
- Conclusion: No — not a reasonable contractor handoff in current form.
- Why: POST-centric contract mirrors internal class graphs; polymorphism without discriminators and circular references increase coupling, testing effort, and integration risk.
- Indicators: ops 15 (POST:15), schemas 77 (objects 63), refs 217, circular 7, maxDepth 3, oneOf branches 15, discriminators 0, score 42.6/100.

## 1. Real-World Implementability
- Domain understandability: Dense, interrelated schemas with cycles require deep domain context.
- Client generation: oneOf without discriminators causes fragile or untyped unions in common generators.
- Endpoint implementation: POST-only orchestration implies RPC over resources; new vendors must mirror server logic.
- Workarounds: Custom mappers, serializers with recursion guards, and hand-written adapters are needed.
- Feasibility: Not realistically feasible without targeted refactoring and governance.

## 2. REST Architecture Appropriateness
- Uniform interface: Lack of safe, cacheable GETs and resource identifiers prevents HTTP caching and linkability.
- Resource modeling: Contract exposes a distributed object model, not stable resource representations.
- Internal coupling: Composition and cycles leak class-model concerns to consumers.
- Impacts: Lower interoperability; limited caching/scalability; larger mocking surface.

## 3. Consumer Burden
- Deserialization: Type resolution by shape/context increases runtime errors and testing effort.
- Coupling/recursion: Circular refs and high $ref density complicate clients and fixtures.
- Test harnesses: Realistic mocks require large interdependent graphs; fixture churn tracks internal changes.
- Semantic ambiguity: POST-only flows conceal behavior, pushing knowledge to docs and tacit understanding.

## 4. Integration Risk & Vendor Lock-In
- Recreating internals: Forces implementers to rebuild server class models, reducing architectural independence.
- Change ripple: Schema changes propagate across integrations and tests.
- Sustainment: Polymorphism without discriminators + cycles create multi-year sustainment drag.

## 5. Recommended Path Forward
- Likely origin: COI-first approach drifted into exposing class hierarchies without a dedicated API architect.
- Strategy:
  1) Define resource boundaries (Events, Detections, Stations, Channels, Timeseries) with stable IDs and GET/PUT/PATCH/DELETE.
  2) Provide faceted/projection views; avoid shipping full aggregates by default.
  3) Add discriminators or simplify polymorphism to explicit types.
  4) Isolate legacy/DAL mapping behind a translation layer; avoid mirroring internals.
  5) Document normalization/masking/compat rules per endpoint.
  6) Establish single-point technical ownership for contract and versioning.
  7) Transition: maintain current endpoints; add resource-oriented ones; deprecate RPC after adoption.

## Waveform Serialization Issue
- Detection: Large JSON arrays of numeric samples (properties: samples) without binary/base64 alternative.
- Expansion: int32 ~2.5x-4x, float64 ~3x-5x size increase vs raw binary.
- CPU/Parsing: Clients must parse and rehydrate all ASCII numbers into binary arrays.
- Precision: Potential float64 round-trip formatting variance (no guaranteed canonical binary preservation).
- Binary alternative present: No
- Recommendation: Provide binary or base64 waveform blocks (application/octet-stream or base64) instead of large JSON numeric arrays; consider container formats (MiniSEED/Arrow).

## Direct Answer
No — not a reasonable contractor handoff now; proceed with the recommended resource-oriented refactor and governance to reduce risk.
