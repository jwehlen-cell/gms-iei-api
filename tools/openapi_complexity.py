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
from typing import Any, Dict, List, Set

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

    return {
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
        },
        "meta": {
            "openapiVersion": spec.get("openapi"),
            "title": spec.get("info", {}).get("title"),
            "version": spec.get("info", {}).get("version"),
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec", help="Path to OpenAPI YAML file")
    ap.add_argument("--json-out", help="Write report to file instead of stdout")
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


if __name__ == "__main__":
    main()
