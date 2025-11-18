# API Architectural Assessment — Event Operations (10-23 Combined)

## Executive Summary
- Conclusion: No — in its current form, this API is not a reasonable handoff to a new contractor with normal cost/schedule/risk. It is implementable only with significant rework and guardrails.
- Why: The contract models a distributed object graph rather than REST resources, relies almost entirely on POST, and mirrors internal class structures. This drives tight coupling, complicates client generation/testing, and undermines interoperability and scalability.
- Indicators (10-23 combined): 15 endpoints, all POST; 77 schemas (63 objects), 217 $refs, 7 circular reference schemas, max depth 3; polymorphism via oneOf (15 branches across 3 nodes), allOf 6, no discriminators; composite complexity score 42.6/100 (Moderate structural complexity, but high architectural risk).

## 1. Real‑World Implementability
- Domain understandability: The API exposes a large, interrelated COI schema (63 object types; 217 refs) with circularities (7 schemas) that require deep domain context to use safely.
- Client generation: Common generators (OpenAPI Generator, Swagger Codegen, NSwag) handle oneOf inconsistently without discriminators. The 15 oneOf branches across 3 nodes, combined with cycles, will yield fragile models, factory code, or fallbacks to `any`/`object` in strongly‑typed clients.
- Endpoint implementation: A POST‑only contract suggests RPC/command style. New teams must replicate server‑side orchestration logic in lockstep with the object model, rather than implementing resource handlers. That significantly raises the barrier for alternative backends.
- Working around polymorphism/cycles: Lack of discriminators means runtime type resolution must be inferred (by shape or context). Circular references increase risk of serialization loops and require custom mappers/test doubles.
- Feasibility rating: Barely feasible without re‑architecting. Clean implementation would require non‑trivial adapters, validators, and mapping layers.

## 2. REST Architecture Appropriateness
- Uniform interface: All 15 operations are POST; there are no canonical resource identifiers, safe (GET) reads, or cacheable responses. This prevents HTTP caching, conditional requests, and linkability.
- Resource modeling: The contract resembles a distributed object model (COI) rather than stable resources with lifecycle semantics. It encourages remote manipulation of aggregates instead of state transfer.
- Coupling to internals: Schemas reflect internal class diagrams (e.g., deep object graphs, allOf composition) and circularities that leak persistence or orchestration details to consumers.
- Impacts: 
  - Interoperability: Low — clients must share internal semantics to participate.
  - Caching/Scalability: Poor — POST‑only blocks HTTP caching and CDN strategies.
  - Testability: Complex — mocks must reproduce coupled object graphs and polymorphic rules.

## 3. Consumer Burden
- Deserialization: OneOf without discriminators forces custom type resolvers. Many generators degrade to untyped unions or manual casts, increasing runtime errors.
- Coupling/recursion: 7 circular ref schemas and high referential density (217 $refs) create fragile client models prone to recursion guards and serialization pitfalls.
- Test harnesses: Meaningful mocks require constructing large, interdependent graphs. Fixture maintenance cost scales with internal model churn.
- Semantic gaps: With POST‑only flows and limited resource affordances, behavior is implicit. This increases reliance on out‑of‑band documentation and tribal knowledge.

## 4. Integration Risk & Vendor Lock‑In
- Recreating internals: External implementers must mirror the server’s class model to interoperate, restricting alternative architectures and technology choices.
- Loss of independence: Any internal schema change cascades into client/server rewrites and test refactors across teams.
- Sustainment horizon: Schema‑driven coupling and polymorphism without crisp resource boundaries create multi‑year sustainment drag and rework after each release.

## 5. Recommended Path Forward
- Likely origins (non‑blaming): The team appears to have pursued a COI first, promoting consistency across UI/backend by exposing class hierarchies directly. Without a dedicated API architect, the design drifted toward a distributed object model.
- Strategy:
  1) Establish resource boundaries: Identify top‑level resources (e.g., Events, Detections, Stations, Channels, Timeseries) with stable identifiers and standard verbs (GET/PUT/PATCH/DELETE).
  2) Introduce faceting/projections: Offer lightweight views for common use cases; avoid shipping full aggregates unless explicitly requested.
  3) Add discriminators or remove polymorphism at the contract: Prefer explicit types or out‑of‑band versioning over shape‑based unions.
  4) Isolate legacy mapping: Keep DAL and legacy class graphs behind a translation layer; the contract should not mirror internals.
  5) Stabilize semantics: Document normalization rules, masking, and compatibility constraints per endpoint.
  6) Governance: Assign a single technical authority to own the API contract, versioning, and change control (resolve cross‑team conflicts and prevent schema leakage).
  7) Transitional plan: Maintain current endpoints; add resource‑oriented equivalents; deprecate RPC‑style calls after adoption.

## Direct Answer
- Is it reasonable to hand this API to another contractor and expect success now? No. The design’s POST‑only interface, internal object graph exposure, and polymorphism without discriminators create high onboarding, implementation, and testing risk. With the recommended resource‑oriented refactor and governance in place, it becomes feasible within normal cost and risk.
