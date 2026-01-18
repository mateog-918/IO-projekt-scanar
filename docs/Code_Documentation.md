# Code Documentation (Sphinx)

Auto-generated code documentation for the SCANAR backend.

---

## Viewing Documentation

1. Navigate to `docs/html/`
2. Open `app.html` in your browser

---

## Documented Modules

- `app.api.auth` - Authentication endpoints
- `app.api.manage_employees` - Employee management
- `app.api.verification` - Verification endpoints
- `app.api.logging` - Logging endpoints
- `app.models.employee` - Employee model
- `app.models.event_log` - Event log model
- `app.services.*` - QR, face recognition, and logging services

---

## Regenerating Documentation

⚠️ **Warning**: This deletes previous documentation!

```bash
cd docs
sphinx-apidoc -o source ../backend/app
make clean
make html
```

**Prerequisites**: `pip install sphinx sphinx-rtd-theme`

**Windows troubleshooting**: If `make` doesn't work, use:
```bash
sphinx-build -b html source build/html
```

---
