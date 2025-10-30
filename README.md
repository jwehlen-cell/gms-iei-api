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