# API Architectural Assessment — FDSN Web Services API

## Executive Summary
- Conclusion: Yes — reasonable handoff with manageable risk.
- Why: POST-centric contract mirrors internal class graphs; polymorphism without discriminators and circular references increase coupling, testing effort, and integration risk.
- Indicators: ops 4 (GET:3, POST:1), schemas 2 (objects 0), refs 66, circular 0, maxDepth 0, oneOf branches 0, discriminators 0, score 29.5/100.

## 1. Real-World Implementability
- Domain understandability: Dense, interrelated schemas with cycles require deep domain context.
- Client generation: oneOf without discriminators causes fragile or untyped unions in common generators.
- Endpoint implementation: POST-only orchestration implies RPC over resources; new vendors must mirror server logic.
- Workarounds: Custom mappers, serializers with recursion guards, and hand-written adapters are needed.
- Feasibility: Feasible with standard practices and modest onboarding.

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

## Direct Answer
Yes — reasonable handoff with manageable risk under standard practices.
