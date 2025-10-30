# GMS IEI API (Combined OpenAPI + Swagger UI)

This repository provides a **unified OpenAPI 3.0 spec** built by merging the Common and Event fragments from your uploaded package, plus ready-to-serve **Swagger UI** and **ReDoc** documentation that can be deployed on **GitHub Pages**.

## What's inside

- `openapi.yaml` — combined OpenAPI spec
- `index.html` — Swagger UI (interactive, Try-It-Out)
- `redoc.html` — ReDoc single-page reference docs
- `.github/workflows/pages.yml` — GitHub Actions workflow to deploy pages
- `.gitignore`, `LICENSE`

## Local preview

Just open `index.html` in a local server (CORS-safe). E.g.:

```bash
python3 -m http.server 8080
# Visit http://localhost:8080
```

Or open `redoc.html` for ReDoc.

## GitHub Pages deployment

1. Create a new GitHub repo (e.g., `gms-iei-api`).
2. Push these files to the `main` branch.
3. In the repo:
   - Go to **Settings → Pages** and set **Source** to **GitHub Actions**.
4. The action in `.github/workflows/pages.yml` will build and publish your site to Pages.
   - Visit `https://<your-org-or-user>.github.io/<repo>/`

## Updating the API

- Edit `openapi.yaml` and commit.
- Swagger UI and ReDoc will auto-refresh on the next Pages build.

## Notes on merge

- Source fragments merged: `common-coi.yaml`, `common-operations.yaml`, `event-coi.yaml`, `event-operations.yaml`.
- If any non-structural conflicts were detected during merge, they're recorded under an **`x-conflicts`** extension path inside `openapi.yaml` so you can review and resolve them manually.

---

Generated on 2025-10-30.