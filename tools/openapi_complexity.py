#!/usr/bin/env python3
"""Compute structural complexity metrics for an OpenAPI specification.

Metrics collected:
  paths.count                     Number of distinct path entries
  operations.count                Total number of HTTP operations
  operations.methods              Breakdown of methods frequencies
  operations.avgParameters        Average parameters per operation (path + op level)
  operations.maxParameters        Max parameters on a single operation
  schemas.count                   Distinct component schema definitions
  schemas.objectCount             Number of object-type schemas
  schemas.avgProperties           Average property count across object schemas
  schemas.maxProperties           Maximum properties in any object schema
  schemas.refCount                Total $ref occurrences (all locations)
  schemas.distinctRefTargets      Distinct internal schema ref targets
  schemas.circularRefSchemas      List of schemas participating in cycles
  schemas.circularRefCount        Count of circular reference schemas
  schemas.maxNestingDepth         Max structural depth (following properties/items/oneOf/allOf/anyOf)

Usage:
  python tools/openapi_complexity.py path/to/spec.yaml [--json-out report.json]

If --json-out is omitted the JSON report is printed to stdout.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict, Counter
from typing import Any, Dict, List, Set, Tuple, Iterable

try:
    import yaml  # type: ignore
except Exception as e:  # pragma: no cover
    print("PyYAML is required: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


HTTP_METHODS = {"get","put","post","delete","options","head","patch","trace"}


def load_spec(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def iter_operations(spec: Dict[str, Any]):
    paths = spec.get("paths", {}) or {}
    for p, item in paths.items():
        if not isinstance(item, dict):
            continue
        path_level_params = item.get("parameters", []) if isinstance(item.get("parameters"), list) else []
        for method, op in item.items():
            if method.lower() in HTTP_METHODS and isinstance(op, dict):
                op_params = op.get("parameters", []) if isinstance(op.get("parameters"), list) else []
                # Combine path-level and operation-level parameters
                total_params = len(path_level_params) + len(op_params)
                yield (p, method.lower(), op, total_params)


def collect_schema_defs(spec: Dict[str, Any]) -> Dict[str, Any]:
    components = spec.get("components", {}) or {}
    schemas = components.get("schemas", {}) or {}
    return {k: v for k, v in schemas.items() if isinstance(v, dict)}


REF_RE = re.compile(r"^#/components/schemas/(?P<name>[^/]+)$")


def find_refs(node: Any) -> List[str]:
    refs = []
    if isinstance(node, dict):
        if "$ref" in node and isinstance(node["$ref"], str):
            refs.append(node["$ref"])
        for v in node.values():
            refs.extend(find_refs(v))
    elif isinstance(node, list):
        for item in node:
            refs.extend(find_refs(item))
    return refs


def iter_schema_nodes(spec: Dict[str, Any]) -> Iterable[Tuple[str, Dict[str, Any]]]:
    """Yield (json_pointer, schema_dict) for all schema nodes in the spec.
    Includes:
      - #/components/schemas/*
      - #/components/parameters/*/schema
      - #/components/requestBodies/*/content/*/schema
      - #/components/responses/*/content/*/schema
      - #/components/headers/*/schema
      - #/paths/<p>/<method>/parameters/*/schema
      - #/paths/<p>/<method>/requestBody/content/*/schema
      - #/paths/<p>/<method>/responses/*/content/*/schema
      - #/paths/<p>/parameters/*/schema (path-level)
    """
    def yield_if_schema(ptr: str, obj: Any):
        if isinstance(obj, dict):
            yield (ptr, obj)

    # components.schemas
    comps = spec.get("components", {}) or {}
    schemas = comps.get("schemas", {}) or {}
    for name, schema in schemas.items():
        if isinstance(schema, dict):
            yield (f"#/components/schemas/{name}", schema)

    # components.parameters
    params = comps.get("parameters", {}) or {}
    for name, param in params.items():
        if isinstance(param, dict):
            sch = param.get("schema")
            if isinstance(sch, dict):
                yield (f"#/components/parameters/{name}/schema", sch)

    # components.requestBodies
    rbs = comps.get("requestBodies", {}) or {}
    for name, rb in rbs.items():
        if isinstance(rb, dict):
            content = rb.get("content", {}) or {}
            if isinstance(content, dict):
                for mt, mt_obj in content.items():
                    if isinstance(mt_obj, dict) and isinstance(mt_obj.get("schema"), dict):
                        yield (f"#/components/requestBodies/{name}/content/{mt}/schema", mt_obj["schema"])

    # components.responses
    resps = comps.get("responses", {}) or {}
    for name, resp in resps.items():
        if isinstance(resp, dict):
            content = resp.get("content", {}) or {}
            if isinstance(content, dict):
                for mt, mt_obj in content.items():
                    if isinstance(mt_obj, dict) and isinstance(mt_obj.get("schema"), dict):
                        yield (f"#/components/responses/{name}/content/{mt}/schema", mt_obj["schema"])

    # components.headers
    headers = comps.get("headers", {}) or {}
    for name, hdr in headers.items():
        if isinstance(hdr, dict) and isinstance(hdr.get("schema"), dict):
            yield (f"#/components/headers/{name}/schema", hdr["schema"])

    # paths
    paths = spec.get("paths", {}) or {}
    for pth, item in paths.items():
        if not isinstance(item, dict):
            continue
        # path-level parameters
        if isinstance(item.get("parameters"), list):
            for i, prm in enumerate(item["parameters"]):
                if isinstance(prm, dict) and isinstance(prm.get("schema"), dict):
                    yield (f"#/paths/{pth}/parameters/{i}/schema", prm["schema"])
        for method, op in item.items():
            if method.lower() not in HTTP_METHODS:
                continue
            if not isinstance(op, dict):
                continue
            # op-level parameters
            if isinstance(op.get("parameters"), list):
                for i, prm in enumerate(op["parameters"]):
                    if isinstance(prm, dict) and isinstance(prm.get("schema"), dict):
                        yield (f"#/paths/{pth}/{method}/parameters/{i}/schema", prm["schema"])
            # requestBody
            rb = op.get("requestBody")
            if isinstance(rb, dict):
                content = rb.get("content", {}) or {}
                if isinstance(content, dict):
                    for mt, mt_obj in content.items():
                        if isinstance(mt_obj, dict) and isinstance(mt_obj.get("schema"), dict):
                            yield (f"#/paths/{pth}/{method}/requestBody/content/{mt}/schema", mt_obj["schema"])
            # responses
            responses = op.get("responses", {}) or {}
            if isinstance(responses, dict):
                for code, resp in responses.items():
                    if isinstance(resp, dict):
                        content = resp.get("content", {}) or {}
                        if isinstance(content, dict):
                            for mt, mt_obj in content.items():
                                if isinstance(mt_obj, dict) and isinstance(mt_obj.get("schema"), dict):
                                    yield (f"#/paths/{pth}/{method}/responses/{code}/content/{mt}/schema", mt_obj["schema"])


def schema_graph(schemas: Dict[str, Any]) -> Dict[str, Set[str]]:
    graph: Dict[str, Set[str]] = {name: set() for name in schemas}
    for name, schema in schemas.items():
        for ref in find_refs(schema):
            m = REF_RE.match(ref)
            if m:
                target = m.group("name")
                graph[name].add(target)
    return graph


def detect_cycles(graph: Dict[str, Set[str]]) -> Set[str]:
    visited: Set[str] = set()
    stack: Set[str] = set()
    cyc: Set[str] = set()

    def dfs(node: str):
        if node in stack:
            cyc.update(stack)
            return
        if node in visited:
            return
        visited.add(node)
        stack.add(node)
        for nxt in graph.get(node, ()):  # follow edges
            dfs(nxt)
        stack.remove(node)

    for n in graph:
        dfs(n)
    return cyc


def schema_depth(schema: Any, seen: Set[int] | None = None) -> int:
    if seen is None:
        seen = set()
    if not isinstance(schema, dict):
        return 0
    obj_id = id(schema)
    if obj_id in seen:
        return 0  # prevent infinite recursion on cycles
    seen.add(obj_id)

    depths = [0]
    # properties depth
    props = schema.get("properties", {}) if isinstance(schema.get("properties"), dict) else {}
    for p in props.values():
        depths.append(1 + schema_depth(p, seen))
    # items depth
    if "items" in schema:
        depths.append(1 + schema_depth(schema["items"], seen))
    # composition keywords
    for key in ("allOf", "anyOf", "oneOf"):
        if key in schema and isinstance(schema[key], list):
            for comp in schema[key]:
                depths.append(1 + schema_depth(comp, seen))
    return max(depths)


def compute_metrics(spec: Dict[str, Any]) -> Dict[str, Any]:
    paths_obj = spec.get("paths", {}) or {}
    path_count = len(paths_obj)
    operations = list(iter_operations(spec))
    op_count = len(operations)
    method_freq = Counter(m for _, m, _, _ in operations)
    param_counts = [pc for *_, pc in operations]
    avg_params = (sum(param_counts) / len(param_counts)) if param_counts else 0.0
    max_params = max(param_counts) if param_counts else 0

    schemas = collect_schema_defs(spec)
    schema_count = len(schemas)
    object_schemas = {k: v for k, v in schemas.items() if v.get("type") == "object"}
    prop_counts = [len(v.get("properties", {}) or {}) for v in object_schemas.values()]
    avg_props = (sum(prop_counts) / len(prop_counts)) if prop_counts else 0.0
    max_props = max(prop_counts) if prop_counts else 0

    all_refs = find_refs(spec)
    internal_schema_refs = [r for r in all_refs if REF_RE.match(r)]
    distinct_ref_targets = sorted({REF_RE.match(r).group("name") for r in internal_schema_refs if REF_RE.match(r)})

    graph = schema_graph(schemas)
    circular = sorted(detect_cycles(graph))

    depths = [schema_depth(s) for s in schemas.values()]
    max_depth = max(depths) if depths else 0

    # Polymorphism metrics (oneOf/anyOf/allOf, discriminators) including nested occurrences
    def count_polymorphism(node: Any) -> Dict[str, int]:
        counts = {
            "union_nodes": 0,           # number of nodes with oneOf/anyOf
            "union_branches": 0,        # total alternatives across oneOf+anyOf
            "max_union_branches": 0,    # max alternatives on a single node
            "allof_items": 0,           # total items across allOf lists
            "discriminators": 0,        # occurrences of discriminator key
            "oneof_nodes": 0,            # number of nodes with oneOf
            "oneof_branches": 0,         # total alternatives across oneOf
            "anyof_nodes": 0,            # number of nodes with anyOf
            "anyof_branches": 0,         # total alternatives across anyOf
        }

        def walk(n: Any):
            if isinstance(n, dict):
                # discriminator
                if "discriminator" in n:
                    counts["discriminators"] += 1
                # oneOf/anyOf
                branches_here = 0
                if isinstance(n.get("oneOf"), list):
                    counts["union_nodes"] += 1
                    counts["oneof_nodes"] += 1
                    counts["oneof_branches"] += len(n["oneOf"])
                    branches_here += len(n["oneOf"])
                if isinstance(n.get("anyOf"), list):
                    counts["union_nodes"] += 1
                    counts["anyof_nodes"] += 1
                    counts["anyof_branches"] += len(n["anyOf"])
                    branches_here += len(n["anyOf"])
                if branches_here:
                    counts["union_branches"] += branches_here
                    if branches_here > counts["max_union_branches"]:
                        counts["max_union_branches"] = branches_here
                # allOf
                if isinstance(n.get("allOf"), list):
                    counts["allof_items"] += len(n["allOf"])
                for v in n.values():
                    walk(v)
            elif isinstance(n, list):
                for it in n:
                    walk(it)

        walk(node)
        return counts

    union_schema_count = 0
    # Counts across all schema nodes in the spec (dedup by JSON pointer)
    visited_ptrs: Set[str] = set()
    union_schema_count = 0
    union_branch_count = 0
    max_union_branches = 0
    allof_usages_total = 0
    discriminator_count = 0

    oneof_nodes_total = 0
    oneof_branches_total = 0
    anyof_nodes_total = 0
    anyof_branches_total = 0
    for ptr, sch in iter_schema_nodes(spec):
        if ptr in visited_ptrs:
            continue
        visited_ptrs.add(ptr)
        c = count_polymorphism(sch)
        union_schema_count += c["union_nodes"]
        union_branch_count += c["union_branches"]
        max_union_branches = max(max_union_branches, c["max_union_branches"])
        allof_usages_total += c["allof_items"]
        discriminator_count += c["discriminators"]
        oneof_nodes_total += c["oneof_nodes"]
        oneof_branches_total += c["oneof_branches"]
        anyof_nodes_total += c["anyof_nodes"]
        anyof_branches_total += c["anyof_branches"]

    # Determine which component schemas are polymorphic by their own structure
    polymorphic_component_targets: Set[str] = set()
    for name, sch in schemas.items():
        c = count_polymorphism(sch)
        if c["union_nodes"] > 0 or c["allof_items"] > 0 or c["discriminators"] > 0:
            polymorphic_component_targets.add(name)

    # Count refs that point to polymorphic components (across entire spec)
    refs_all_nodes: List[str] = []
    for _, sch in iter_schema_nodes(spec):
        refs_all_nodes.extend(find_refs(sch))
    poly_ref_targets: List[str] = []
    for r in refs_all_nodes:
        m = REF_RE.match(r)
        if m:
            t = m.group("name")
            if t in polymorphic_component_targets:
                poly_ref_targets.append(t)
    distinct_poly_ref_targets = sorted(set(poly_ref_targets))

    report: Dict[str, Any] = {
        "paths": {"count": path_count},
        "operations": {
            "count": op_count,
            "methods": dict(method_freq),
            "avgParameters": round(avg_params, 2),
            "maxParameters": max_params,
        },
        "schemas": {
            "count": schema_count,
            "objectCount": len(object_schemas),
            "avgProperties": round(avg_props, 2),
            "maxProperties": max_props,
            "refCount": len(all_refs),
            "distinctRefTargets": distinct_ref_targets,
            "circularRefSchemas": circular,
            "circularRefCount": len(circular),
            "maxNestingDepth": max_depth,
            "polymorphism": {
                "unionSchemaCount": union_schema_count,
                "unionBranchCount": union_branch_count,
                "maxUnionBranches": max_union_branches,
                "allOfUsages": allof_usages_total,
                "discriminatorCount": discriminator_count,
                "oneOfSchemaCount": oneof_nodes_total,
                "oneOfBranchCount": oneof_branches_total,
                "anyOfSchemaCount": anyof_nodes_total,
                "anyOfBranchCount": anyof_branches_total,
                "polymorphicRefCount": len(poly_ref_targets),
                "distinctPolymorphicRefTargets": distinct_poly_ref_targets,
                "scannedSchemaNodes": len(visited_ptrs),
            },
        },
        "meta": {
            "openapiVersion": spec.get("openapi"),
            "title": spec.get("info", {}).get("title"),
            "version": spec.get("info", {}).get("version"),
        },
    }

    # Compute a composite complexity score on a 0-100 scale
    def norm_log(x: float, k: float) -> float:
        # Smoothly grow with diminishing returns, saturate near k
        if k <= 0:
            return 0.0
        import math
        return min(1.0, (math.log10(1 + max(0.0, x)) / math.log10(1 + k)))

    ops = report["operations"]["count"]
    paths = report["paths"]["count"]
    schemas_cnt = report["schemas"]["count"]
    refs_cnt = report["schemas"]["refCount"]
    avg_params_sc = report["operations"]["avgParameters"]
    max_params_sc = report["operations"]["maxParameters"]
    max_depth_sc = report["schemas"]["maxNestingDepth"]
    circular_sc = report["schemas"]["circularRefCount"]
    poly = report["schemas"]["polymorphism"]
    union_branches = poly["unionBranchCount"]
    allof_total = poly["allOfUsages"]
    discriminator_cnt = poly["discriminatorCount"]

    # Normalizations (0..1)
    n_ops = norm_log(ops, 500)
    n_paths = norm_log(paths, 300)
    n_schemas = norm_log(schemas_cnt, 500)
    n_refs = norm_log(refs_cnt, 2000)
    n_avg_params = min(1.0, (avg_params_sc or 0) / 10.0)
    n_max_params = min(1.0, (max_params_sc or 0) / 20.0)
    n_depth = min(1.0, (max_depth_sc or 0) / 10.0)
    n_circular = min(1.0, (circular_sc or 0) / 10.0)

    # Weights sum to 100; include polymorphism aspects
    weights = {
        "ops": 22.0,
        "schemas": 18.0,
        "refs": 12.0,
        "paths": 8.0,
        "avg_params": 8.0,
        "depth": 10.0,
        "max_params": 4.0,
        "circular": 3.0,
        "poly_union": 8.0,
        "poly_allof": 4.0,
        "poly_discriminator": 3.0,
    }

    # Normalizations for polymorphism
    n_poly_union = min(1.0, (union_branches or 0) / 100.0)
    n_poly_allof = min(1.0, (allof_total or 0) / 50.0)
    n_poly_discriminator = min(1.0, (discriminator_cnt or 0) / 25.0)

    score = (
        n_ops * weights["ops"]
        + n_schemas * weights["schemas"]
        + n_refs * weights["refs"]
        + n_paths * weights["paths"]
        + n_avg_params * weights["avg_params"]
        + n_depth * weights["depth"]
        + n_max_params * weights["max_params"]
        + n_circular * weights["circular"]
        + n_poly_union * weights["poly_union"]
        + n_poly_allof * weights["poly_allof"]
        + n_poly_discriminator * weights["poly_discriminator"]
    )

    score = round(float(score), 1)

    def label_for_score(s: float) -> str:
        if s < 25:
            return "Low"
        if s < 50:
            return "Moderate"
        if s < 75:
            return "High"
        return "Very High"

    # Build a concise human-readable summary
    methods = report["operations"]["methods"]
    method_parts = [f"{m.upper()}:{c}" for m, c in sorted(methods.items())]
    title = report["meta"].get("title") or "(untitled)"
    version = report["meta"].get("version") or "(unknown)"
    summary = (
        f"Spec: {title} v{version} | "
        f"Paths: {paths}, Ops: {ops} ({', '.join(method_parts)}) | "
        f"Schemas: {schemas_cnt} (objects: {report['schemas']['objectCount']}, avgProps: {report['schemas']['avgProperties']}, maxProps: {report['schemas']['maxProperties']}) | "
        f"Refs: {refs_cnt}, DistinctRefs: {len(report['schemas']['distinctRefTargets'])}, Circular: {circular_sc} | "
        f"MaxDepth: {max_depth_sc} | Poly: oneOf {report['schemas']['polymorphism']['oneOfBranchCount']}, anyOf {report['schemas']['polymorphism']['anyOfBranchCount']}, allOf {allof_total}, discrim {discriminator_cnt} | "
        f"Score: {score}/100 ({label_for_score(score)})"
    )

    report["complexityScore"] = score
    report["complexityLabel"] = label_for_score(score)
    report["summary"] = summary

    # Waveform serialization detection heuristic
    # Look for large numeric sample arrays that likely represent binary int32/float64 expanded to JSON.
    sample_array_props: List[Dict[str, Any]] = []
    binary_alt_present = False
    # Keywords that suggest waveform sample arrays
    sample_keys = {"samples","waveform","data","values"}
    for ptr, sch in iter_schema_nodes(spec):
        if not isinstance(sch, dict):
            continue
        props = sch.get("properties") if isinstance(sch.get("properties"), dict) else {}
        for k, v in props.items():
            if k.lower() in sample_keys and isinstance(v, dict):
                # Match array<number>/<integer> without explicit binary/base64 encoding
                items = v.get("items") if isinstance(v.get("items"), dict) else None
                if v.get("type") == "array" and items and items.get("type") in {"number","integer"}:
                    fmt = items.get("format")
                    sample_array_props.append({"schemaPointer": ptr, "property": k, "itemType": items.get("type"), "itemFormat": fmt})
        # Check for potential binary alternatives (presence of format byte/binary or contentEncoding base64)
        if isinstance(props, dict):
            for v in props.values():
                if isinstance(v, dict):
                    if v.get("format") in {"byte","binary"} or v.get("contentEncoding") == "base64":
                        binary_alt_present = True
    # Another indicator: media types offering application/octet-stream
    paths_obj = spec.get("paths", {}) or {}
    for pth, item in paths_obj.items():
        if isinstance(item, dict):
            for method, op in item.items():
                if method.lower() in HTTP_METHODS and isinstance(op, dict):
                    for section in ("requestBody","responses"):
                        sec_obj = op.get(section)
                        if isinstance(sec_obj, dict):
                            content = sec_obj.get("content", {}) or {}
                            if isinstance(content, dict):
                                if any(mt.lower() == "application/octet-stream" for mt in content.keys()):
                                    binary_alt_present = True
    if sample_array_props:
        expansion_factor_estimate = {
            "int32": "~2.5x-4x",
            "float64": "~3x-5x"
        }
        report["waveformSerialization"] = {
            "issueDetected": True,
            "sampleArrayProperties": sample_array_props,
            "binaryAlternativePresent": binary_alt_present,
            "expansionFactorEstimate": expansion_factor_estimate,
            "precisionRiskFloat64": True,  # absence of guaranteed exact round-trip formatting
            "recommendation": "Provide binary or base64 waveform blocks (application/octet-stream or base64) instead of large JSON numeric arrays; consider container formats (MiniSEED/Arrow)."
        }
    else:
        report["waveformSerialization"] = {"issueDetected": False}

    return report


def _render_assessment_md(report: Dict[str, Any]) -> str:
    ops = report["operations"]["count"]
    methods = report["operations"]["methods"]
    post_only = bool(ops) and set(methods.keys()) == {"post"}
    schemas_cnt = report["schemas"]["count"]
    obj_cnt = report["schemas"]["objectCount"]
    refs_cnt = report["schemas"]["refCount"]
    circ_cnt = report["schemas"]["circularRefCount"]
    max_depth = report["schemas"]["maxNestingDepth"]
    poly = report["schemas"]["polymorphism"]
    union_branches = poly.get("unionBranchCount", 0) or 0
    union_nodes = poly.get("unionSchemaCount", 0) or 0
    discrim_cnt = poly.get("discriminatorCount", 0) or 0
    score = float(report.get("complexityScore", 0.0) or 0.0)
    title = report.get("meta", {}).get("title") or "(untitled)"
    version = report.get("meta", {}).get("version") or "(unknown)"

    # Heuristic feasibility classification
    not_feasible = post_only and union_branches >= 10 and discrim_cnt == 0 and circ_cnt >= 5 and refs_cnt >= 150
    barely_feasible = (post_only or union_branches > 0 or circ_cnt > 0 or refs_cnt >= 100)
    if not_feasible:
        conclusion = "No — not a reasonable contractor handoff in current form."
        feasibility = "Not realistically feasible without targeted refactoring and governance."
    elif barely_feasible:
        conclusion = "Risky — possible but only with non-trivial guardrails."
        feasibility = "Barely feasible; expect adapters, validators, and mapping layers."
    else:
        conclusion = "Yes — reasonable handoff with manageable risk."
        feasibility = "Feasible with standard practices and modest onboarding."

    md = []
    md.append(f"# API Architectural Assessment — {title}\n")
    md.append("## Executive Summary")
    md.append(f"- Conclusion: {conclusion}")
    md.append("- Why: POST-centric contract mirrors internal class graphs; polymorphism without discriminators and circular references increase coupling, testing effort, and integration risk.")
    md.append(
        f"- Indicators: ops {ops} ({', '.join(k.upper()+':'+str(v) for k,v in methods.items())}), "
        f"schemas {schemas_cnt} (objects {obj_cnt}), refs {refs_cnt}, circular {circ_cnt}, maxDepth {max_depth}, oneOf branches {union_branches}, discriminators {discrim_cnt}, score {score}/100.\n"
    )

    md.append("## 1. Real-World Implementability")
    md.append("- Domain understandability: Dense, interrelated schemas with cycles require deep domain context.")
    md.append("- Client generation: oneOf without discriminators causes fragile or untyped unions in common generators.")
    md.append("- Endpoint implementation: POST-only orchestration implies RPC over resources; new vendors must mirror server logic.")
    md.append("- Workarounds: Custom mappers, serializers with recursion guards, and hand-written adapters are needed.")
    md.append(f"- Feasibility: {feasibility}\n")

    md.append("## 2. REST Architecture Appropriateness")
    md.append("- Uniform interface: Lack of safe, cacheable GETs and resource identifiers prevents HTTP caching and linkability.")
    md.append("- Resource modeling: Contract exposes a distributed object model, not stable resource representations.")
    md.append("- Internal coupling: Composition and cycles leak class-model concerns to consumers.")
    md.append("- Impacts: Lower interoperability; limited caching/scalability; larger mocking surface.\n")

    md.append("## 3. Consumer Burden")
    md.append("- Deserialization: Type resolution by shape/context increases runtime errors and testing effort.")
    md.append("- Coupling/recursion: Circular refs and high $ref density complicate clients and fixtures.")
    md.append("- Test harnesses: Realistic mocks require large interdependent graphs; fixture churn tracks internal changes.")
    md.append("- Semantic ambiguity: POST-only flows conceal behavior, pushing knowledge to docs and tacit understanding.\n")

    md.append("## 4. Integration Risk & Vendor Lock-In")
    md.append("- Recreating internals: Forces implementers to rebuild server class models, reducing architectural independence.")
    md.append("- Change ripple: Schema changes propagate across integrations and tests.")
    md.append("- Sustainment: Polymorphism without discriminators + cycles create multi-year sustainment drag.\n")

    md.append("## 5. Recommended Path Forward")
    md.append("- Likely origin: COI-first approach drifted into exposing class hierarchies without a dedicated API architect.")
    md.append("- Strategy:")
    md.append("  1) Define resource boundaries (Events, Detections, Stations, Channels, Timeseries) with stable IDs and GET/PUT/PATCH/DELETE.")
    md.append("  2) Provide faceted/projection views; avoid shipping full aggregates by default.")
    md.append("  3) Add discriminators or simplify polymorphism to explicit types.")
    md.append("  4) Isolate legacy/DAL mapping behind a translation layer; avoid mirroring internals.")
    md.append("  5) Document normalization/masking/compat rules per endpoint.")
    md.append("  6) Establish single-point technical ownership for contract and versioning.")
    md.append("  7) Transition: maintain current endpoints; add resource-oriented ones; deprecate RPC after adoption.\n")

    # Inject waveform serialization section if detected
    wf = report.get("waveformSerialization", {})
    if wf.get("issueDetected"):
        md.append("## Waveform Serialization Issue")
        md.append("- Detection: Large JSON arrays of numeric samples (properties: " + ", ".join(p["property"] for p in wf.get("sampleArrayProperties", [])) + ") without binary/base64 alternative.")
        md.append(f"- Expansion: int32 {wf['expansionFactorEstimate']['int32']}, float64 {wf['expansionFactorEstimate']['float64']} size increase vs raw binary.")
        md.append("- CPU/Parsing: Clients must parse and rehydrate all ASCII numbers into binary arrays.")
        md.append("- Precision: Potential float64 round-trip formatting variance (no guaranteed canonical binary preservation).")
        md.append("- Binary alternative present: " + ("Yes" if wf.get("binaryAlternativePresent") else "No"))
        md.append("- Recommendation: " + wf.get("recommendation", "Provide binary transfer mode."))
        md.append("")

    md.append("## Direct Answer")
    if not_feasible:
        md.append("No — not a reasonable contractor handoff now; proceed with the recommended resource-oriented refactor and governance to reduce risk.")
    elif barely_feasible:
        md.append("Risky — feasible with non-trivial guardrails (adapters, validators, mapping layers) and governance.")
    else:
        md.append("Yes — reasonable handoff with manageable risk under standard practices.")

    return "\n".join(md) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec", help="Path to OpenAPI YAML file")
    ap.add_argument("--json-out", help="Write report to file instead of stdout")
    ap.add_argument("--assessment-out", help="Write qualitative assessment Markdown to this file")
    args = ap.parse_args()

    spec = load_spec(args.spec)
    report = compute_metrics(spec)
    out = json.dumps(report, indent=2, sort_keys=False)
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as f:
            f.write(out)
        print(f"Wrote complexity report to {args.json_out}")
    else:
        print(out)
        # Also print a concise human-readable summary and score for quick scanning
        print("\n=== Summary ===")
        print(report.get("summary", ""))

    if args.assessment_out:
        md = _render_assessment_md(report)
        with open(args.assessment_out, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"Wrote assessment to {args.assessment_out}")


if __name__ == "__main__":
    main()
