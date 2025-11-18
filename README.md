# GMS IEI API Documentation

This repository provides a **unified OpenAPI 3.0 specification** for the GMS IEI API with interactive documentation powered by **Swagger UI** and **ReDoc**, automatically deployed via **GitHub Pages**.

## 🌐 Live Documentation

**📖 Interactive API Documentation**: [https://jwehlen-cell.github.io/gms-iei-api/](https://jwehlen-cell.github.io/gms-iei-api/)

## 📁 Repository Contents

- **`openapi.yaml`** — Unified OpenAPI 3.0 specification
- **`index.html`** — Swagger UI (interactive documentation with "Try It Out" functionality)
- **`redoc.html`** — ReDoc single-page reference documentation
- **`.github/workflows/pages.yml`** — GitHub Actions workflow for automatic deployment
- **`.nojekyll`** — Ensures proper GitHub Pages deployment
- **`LICENSE`** — Repository license

## 🚀 Quick Start

### Local Development

To preview the documentation locally:

```bash
# Start a local HTTP server
python3 -m http.server 8000

# Visit the documentation
open http://localhost:8000
```

The Swagger UI will be available at the root URL, or you can access ReDoc directly at `http://localhost:8000/redoc.html`.

### GitHub Pages Deployment

The documentation is automatically deployed to GitHub Pages via GitHub Actions:

1. **Automatic Deployment**: Every push to the `main` branch triggers a deployment
2. **Live URL**: [https://jwehlen-cell.github.io/gms-iei-api/](https://jwehlen-cell.github.io/gms-iei-api/)
3. **Deployment Status**: Check [Actions tab](https://github.com/jwehlen-cell/gms-iei-api/actions) for build status

#### Manual Setup (if needed)

If setting up in a new repository:

1. Fork or clone this repository
2. Push to your GitHub repository's `main` branch  
3. Go to **Settings → Pages** in your repository
4. Set **Source** to **GitHub Actions**
5. The workflow will automatically deploy your documentation

## 🔧 Updating the API Documentation

1. **Edit the OpenAPI specification**: Modify `openapi.yaml`
2. **Commit and push**: Changes will automatically trigger a new deployment
3. **Documentation updates**: Swagger UI and ReDoc will reflect changes within 2-3 minutes

```bash
# Make your changes to openapi.yaml
git add openapi.yaml
git commit -m "Update API specification"
git push origin main
```

## 🛠️ Troubleshooting

### GitHub Pages 404 Error
If you encounter a 404 error:

1. **Check repository visibility**: Repository must be public (or you need GitHub Pro/Team for private repos)
2. **Verify Pages settings**: Go to Settings → Pages, ensure source is set to "GitHub Actions"
3. **Check deployment status**: Visit the [Actions tab](https://github.com/jwehlen-cell/gms-iei-api/actions) to see if deployment succeeded
4. **Wait for deployment**: Initial deployment can take 5-10 minutes

### Local Development Issues
- **CORS errors**: Always use a local HTTP server, don't open `index.html` directly in browser
- **File not found**: Ensure you're running the server from the repository root directory

## 📋 API Specification Details

This OpenAPI specification was created by merging multiple API fragments:

- **Source fragments**: `common-coi.yaml`, `common-operations.yaml`, `event-coi.yaml`, `event-operations.yaml`
- **Version**: OpenAPI 3.0.3
- **API Title**: GMS IEI API (Combined)
- **Conflict resolution**: Any merge conflicts are documented under `x-conflicts` extension in the YAML

## 📊 Complexity Metrics

This repo includes a Python tool that computes structural complexity of an OpenAPI spec with a final score and human summary.

- Tool: `tools/openapi_complexity.py`
- Output: JSON containing metrics plus `complexityScore` (0–100), `complexityLabel`, and a `summary` string.

Scoring considers the following (normalized and weighted):
- Operations and paths volume
- Schema volume and reference count
- Parameters per operation (avg/max)
- Structural depth and circular references
- Polymorphism: total union branches (`oneOf`/`anyOf`), `allOf` usages, and discriminator count

### Run on current specs

Create a local Python environment and install PyYAML (first time only):

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install pyyaml
```

Generate reports:

```bash
# Root combined API
./.venv/bin/python tools/openapi_complexity.py openapi.yaml --json-out complexity-openapi.json

# Historical combined (as-is)
./.venv/bin/python tools/openapi_complexity.py gms-iei-combined.yaml --json-out complexity-combined.json

# Historical combined (fixed refs)
./.venv/bin/python tools/openapi_complexity.py gms-iei-combined.fixed.yaml --json-out complexity-combined-fixed.json
```

Example summary (printed after the JSON):

```
=== Summary ===
Spec: GMS IEI API (Combined) v2.0.0-modern | Paths: 14, Ops: 17 (GET:9, POST:8) | Schemas: 61 (objects: 40, avgProps: 4.58, maxProps: 14) | Refs: 142, DistinctRefs: 43, Circular: 4 | MaxDepth: 2 | Score: 54.1/100 (High)
```

### Build a 10-23 combined spec (with operations) and score it

The file `imported/10-23/openapi-10-23-bundled.yaml` contains schemas with `paths: {}`. To include the 10-23 domain POST operations, concatenate all domain Operations + COI YAMLs and normalize refs:

```bash
# Concatenate domain operations and COI specs into one file
cat \
imported/10-23/gms-iei-req-2025-10-23/Common/OpenAPISpec/common-operations.yaml \
imported/10-23/gms-iei-req-2025-10-23/Common/OpenAPISpec/common-coi.yaml \
imported/10-23/gms-iei-req-2025-10-23/Event/OpenAPISpec/event-operations.yaml \
imported/10-23/gms-iei-req-2025-10-23/Event/OpenAPISpec/event-coi.yaml \
imported/10-23/gms-iei-req-2025-10-23/SignalDetection/OpenAPISpec/signal-detection-operations.yaml \
imported/10-23/gms-iei-req-2025-10-23/SignalDetection/OpenAPISpec/signal-detection-coi.yaml \
imported/10-23/gms-iei-req-2025-10-23/StationDefinition/OpenAPISpec/station-definition-operations.yaml \
imported/10-23/gms-iei-req-2025-10-23/StationDefinition/OpenAPISpec/station-definition-coi.yaml \
imported/10-23/gms-iei-req-2025-10-23/Waveform/OpenAPISpec/waveform-operations.yaml \
imported/10-23/gms-iei-req-2025-10-23/Waveform/OpenAPISpec/waveform-coi.yaml \
imported/10-23/gms-iei-req-2025-10-23/Intervals/OpenAPISpec/workflow-operations.yaml \
imported/10-23/gms-iei-req-2025-10-23/Intervals/OpenAPISpec/workflow-coi.yaml \
> imported/10-23/gms-iei-10-23-combined.yaml

# Normalize refs and merge into a single valid OpenAPI file
./.venv/bin/python tools/fix_combined_openapi.py imported/10-23/gms-iei-10-23-combined.yaml

# Compute complexity
./.venv/bin/python tools/openapi_complexity.py imported/10-23/gms-iei-10-23-combined.fixed.yaml \
	--json-out complexity-10-23-combined.json
```

Notes:
- The concatenation step is naive (no `---` separators); the fixer handles it and rewrites external `$ref` paths to internal refs.
- The previously bundled `openapi-10-23-bundled.yaml` (schemas only) will yield 0 operations; use the combined file above to include POST operations.

## 📝 License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes to `openapi.yaml`
4. Test locally using the local development setup
5. Commit your changes: `git commit -am 'Add your feature'`
6. Push to the branch: `git push origin feature/your-feature`
7. Submit a pull request

---

**Last updated**: October 29, 2025  
**Generated documentation**: [https://jwehlen-cell.github.io/gms-iei-api/](https://jwehlen-cell.github.io/gms-iei-api/)