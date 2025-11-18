#!/usr/bin/env python3
"""
Fix a concatenated OpenAPI YAML (multiple documents back-to-back) into a single
valid OpenAPI file with all references internal to the file.

Usage:
  python tools/fix_combined_openapi.py gms-iei-combined.yaml [--in-place]

By default, writes a new file alongside the input with suffix ".fixed.yaml" and
creates a ".bak" backup of the original if --in-place is used.
"""

from __future__ import annotations

import re
import sys
from copy import deepcopy

try:
    import yaml  # type: ignore
except Exception as e:
    print("ERROR: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


def split_concatenated_docs(text: str) -> list[str]:
    """Split a file that contains multiple OpenAPI YAML docs concatenated without
    '---' separators. We split on lines that start with 'openapi:' at column 0.
    The first chunk may include a BOM or leading blank lines.
    """
    # Find all start indices of lines beginning with 'openapi:' (allow optional BOM/whitespace)
    starts = [m.start() for m in re.finditer(r"(?m)^openapi:\s*", text)]
    if not starts:
        return [text]
    chunks = []
    for i, s in enumerate(starts):
        e = starts[i + 1] if i + 1 < len(starts) else len(text)
        # include possible leading newlines for the first document
        if i == 0:
            # backtrack to the prior newline if there are blank lines before
            # but keep it simple and just start from beginning of file
            chunk = text[:e]
        else:
            chunk = text[s:e]
        chunks.append(chunk.strip("\n"))
    return chunks


def deep_merge(dst: dict, src: dict):
    """Deep-merge dict src into dst (modifies dst). Lists are concatenated with de-dup.
    Dict values are merged recursively; scalars prefer existing dst value.
    """
    for k, v in src.items():
        if v is None:
            continue
        if k not in dst:
            dst[k] = deepcopy(v)
        else:
            if isinstance(dst[k], dict) and isinstance(v, dict):
                deep_merge(dst[k], v)
            elif isinstance(dst[k], list) and isinstance(v, list):
                # merge lists with de-dup based on repr
                seen = {repr(x) for x in dst[k]}
                for item in v:
                    r = repr(item)
                    if r not in seen:
                        dst[k].append(item)
                        seen.add(r)
            else:
                # keep existing dst value; do not overwrite top-level scalars silently
                # (we could add a conflict log here if needed)
                pass


def merge_docs(docs: list[dict]) -> dict:
    if not docs:
        raise ValueError("No YAML documents to merge")

    # Start with the first document as baseline
    result = deepcopy(docs[0]) if isinstance(docs[0], dict) else {}
    if not isinstance(result, dict):
        result = {}

    # Ensure required top-level sections exist
    result.setdefault("openapi", "3.0.3")
    result.setdefault("info", {"title": "Combined OpenAPI", "version": "0.0.0"})
    result.setdefault("paths", {})
    result.setdefault("components", {})

    # Initialize standard components keys for OAS 3.0.x
    for key in [
        "schemas",
        "parameters",
        "responses",
        "requestBodies",
        "headers",
        "securitySchemes",
        "examples",
        "links",
        "callbacks",
    ]:
        result["components"].setdefault(key, {})
    # Only OAS 3.1 supports components.pathItems; add conditionally
    openapi_ver = str(result.get("openapi", "3.0.3"))
    if openapi_ver.startswith("3.1"):
        result["components"].setdefault("pathItems", {})

    # Merge subsequent documents
    for doc in docs[1:]:
        if not isinstance(doc, dict):
            continue
        # Merge paths
        if "paths" in doc and isinstance(doc["paths"], dict):
            deep_merge(result["paths"], doc["paths"])

        # Merge components
        if "components" in doc and isinstance(doc["components"], dict):
            for comp_key, comp_val in doc["components"].items():
                if isinstance(comp_val, dict):
                    result["components"].setdefault(comp_key, {})
                    deep_merge(result["components"][comp_key], comp_val)

        # Merge tags
        if "tags" in doc and isinstance(doc["tags"], list):
            result.setdefault("tags", [])
            existing_names = {t.get("name") for t in result["tags"] if isinstance(t, dict)}
            for t in doc["tags"]:
                if isinstance(t, dict) and t.get("name") not in existing_names:
                    result["tags"].append(t)
                    existing_names.add(t.get("name"))

        # Merge servers
        if "servers" in doc and isinstance(doc["servers"], list):
            result.setdefault("servers", [])
            existing_urls = {s.get("url") for s in result["servers"] if isinstance(s, dict)}
            for s in doc["servers"]:
                if isinstance(s, dict) and s.get("url") not in existing_urls:
                    result["servers"].append(s)
                    existing_urls.add(s.get("url"))

    # If using 3.0.x, ensure pathItems is not present (some validators flag it)
    if not openapi_ver.startswith("3.1"):
        result.get("components", {}).pop("pathItems", None)

    # Optionally drop empty components sections to keep the file tidy
    if "components" in result and isinstance(result["components"], dict):
        for k in list(result["components"].keys()):
            v = result["components"][k]
            if isinstance(v, dict) and not v:
                # keep critical ones (schemas, parameters, responses) even if empty
                if k not in {"schemas", "parameters", "responses"}:
                    result["components"].pop(k, None)

    return result


def rewrite_internal_refs(node):
    """Walk the structure and rewrite external $ref like './x.yaml#/components/schemas/Foo'
    to '#/components/schemas/Foo'. Leaves already-internal '#/components/...' refs intact.
    """
    if isinstance(node, dict):
        # rewrite $ref if needed
        if "$ref" in node and isinstance(node["$ref"], str):
            ref = node["$ref"]
            m = re.match(r"^(?!#)([^#]+)#/(.+)$", ref)
            if m:
                node["$ref"] = "#/%s" % m.group(2)
        for k, v in list(node.items()):
            rewrite_internal_refs(v)
    elif isinstance(node, list):
        for item in node:
            rewrite_internal_refs(item)


def main():
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="Path to concatenated OpenAPI YAML")
    ap.add_argument("--in-place", action="store_true", help="Overwrite input file (creates .bak backup)")
    args = ap.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        text = f.read()

    # Split into pseudo-documents and parse each
    chunks = split_concatenated_docs(text)
    docs = []
    for i, ch in enumerate(chunks):
        try:
            # Support multiple '---' docs within a chunk
            loaded = list(yaml.safe_load_all(ch))
            for d in loaded:
                if d is not None:
                    docs.append(d)
        except Exception as e:
            print(f"WARNING: Failed to parse chunk {i}: {e}", file=sys.stderr)

    if not docs:
        print("ERROR: No documents parsed; aborting.", file=sys.stderr)
        sys.exit(2)

    combined = merge_docs(docs)
    rewrite_internal_refs(combined)

    # Ensure only one openapi root
    if not combined.get("openapi"):
        combined["openapi"] = "3.0.3"

    out_text = yaml.safe_dump(combined, sort_keys=False, allow_unicode=True)

    if args["in_place"] if isinstance(args, dict) else args.in_place:
        # backup
        bak = args.input + ".bak"
        with open(bak, "w", encoding="utf-8") as f:
            f.write(text)
        with open(args.input, "w", encoding="utf-8") as f:
            f.write(out_text)
        print(f"Wrote merged OpenAPI to {args.input} (backup at {bak})")
    else:
        out_path = re.sub(r"\.ya?ml$", "", args.input) + ".fixed.yaml"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(out_text)
        print(f"Wrote merged OpenAPI to {out_path}")


if __name__ == "__main__":
    main()
