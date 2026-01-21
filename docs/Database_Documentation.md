# Database Documentation

## Overview

SCANAR uses SQLite as its local embedded database, storing employee data, access logs, and associated files in a structured directory layout.

---

## Database Location

**Main Database File:**
```
instance/scanar.db
```
**Database models**
```
backend\app\models
```

- **Type:** SQLite 3.x

---

## File Storage Locations

### QR Codes
```
static/qr_codes/
```

### Employee Face Images
```
static/face_images/
```

### Verification Attempt Captures
```
static/face_images/
```

---