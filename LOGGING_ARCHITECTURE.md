# Event Logging System - Visual Architecture

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                          FRONTEND                               │
│  (React/Vue app with QR scanner + camera)                       │
└──────────────────────────────────────────────────────────────────┘
                            │
                   ┌────────┴────────┐
                   │                 │
         ┌─────────▼──────┐  ┌──────▼──────────┐
         │  /api/verification/qr   │  /api/verification/employees/{id}/match  │
         │  (with QR data + image) │  (with face image)                      │
         └─────────┬──────┘  └──────┬──────────┘
                   │                │
     ┌─────────────▼────────────────▼──────────────┐
     │    VERIFICATION ENDPOINTS                   │
     │  (app/api/verification.py)                  │
     │                                             │
     │  ✓ validate_qr_code()                      │
     │  ✓ matches_face_image()                    │
     └─────────────┬─────────────────────┬────────┘
                   │                     │
     ┌─────────────▼────────────────────▼──────────────────┐
     │    LOGGING SERVICE (NEW)                            │
     │  (app/services/logging_service.py)                  │
     │                                                     │
     │  ✓ log_event() - Create log entry                 │
     │  ✓ save_image() - Store image file                │
     └─────────────┬────────────────────────┬─────────────┘
                   │                        │
         ┌─────────▼──────┐      ┌─────────▼──────┐
         │ DATABASE       │      │  FILE SYSTEM   │
         │ instance/      │      │  static/logs/  │
         │ scanar.db      │      │                │
         │                │      │  ├─ INVALID_QR/│
         │ event_logs     │      │  ├─ FACE_      │
         │ table (NEW)    │      │  │  MISMATCH/  │
         │                │      │  ├─ VERIFICATION│
         │ ├─ id          │      │  │  _SUCCESS/  │
         │ ├─ event_type  │      │  ├─ QR_SCANNED/│
         │ ├─ employee_id │      │  └─ FACE_      │
         │ ├─ qr_hash     │      │     SCANNED/   │
         │ ├─ image_path  │      │                │
         │ ├─ message     │      │  (PNG images)  │
         │ └─ timestamp   │      └────────────────┘
         └────────┬───────┘
                  │
     ┌────────────▼──────────────────────┐
     │  LOGGING API ENDPOINTS (NEW)       │
     │  (app/api/logging.py)              │
     │                                    │
     │  GET /api/logs/                   │
     │  GET /api/logs/type/{type}        │
     │  GET /api/logs/employee/{id}      │
     │  GET /api/logs/date-range         │
     │  GET /api/logs/statistics         │
     │  GET /api/logs/image/{id}         │
     └────────────┬───────────────────────┘
                  │
         ┌────────▼──────────┐
         │   FRONTEND        │
         │  Dashboard/       │
         │  Analytics/       │
         │  Reports          │
         └───────────────────┘
```

## Event Flow Examples

### Example 1: Valid QR Scan → Successful Verification

```
User scans QR Code
       │
       ▼
POST /api/verification/qr (qr_data + image)
       │
       ▼
QRService.validate_qr_code() ✓ Found
       │
       ├─► LoggingService.log_event(QR_SCANNED)
       │   - Log created: id=101
       │   - Image saved: static/logs/QR_SCANNED/QR_SCANNED_5_*.png
       │
       ▼
Response: {success: true, employee: {...}}
       │
       ▼
User scans Face
       │
       ▼
POST /api/verification/employees/5/match (image)
       │
       ▼
matches_face_image() ✓ Match Found
       │
       ├─► LoggingService.log_event(VERIFICATION_SUCCESS)
       │   - Log created: id=102
       │   - Image saved: static/logs/VERIFICATION_SUCCESS/VERIFICATION_SUCCESS_5_*.png
       │
       ▼
Response: {match: true, log_id: 102}
       │
       ▼
✓ SUCCESSFUL VERIFICATION
```

### Example 2: Invalid QR Scan

```
User scans invalid QR Code
       │
       ▼
POST /api/verification/qr (qr_data + image)
       │
       ▼
QRService.validate_qr_code() ✗ Not Found
       │
       ├─► LoggingService.log_event(INVALID_QR)
       │   - Log created: id=103
       │   - Image saved: static/logs/INVALID_QR/INVALID_QR_*.png
       │
       ▼
Response: {success: false, message: "QR not found"}
       │
       ▼
✗ BLOCKED - QR Code Invalid
```

### Example 3: Face Mismatch (Wrong Person)

```
User scans valid QR Code (Employee A)
       │
       ▼
POST /api/verification/qr ✓
       │
       ├─► LoggingService.log_event(QR_SCANNED)
       │
       ▼
User scans face (Actually Employee B)
       │
       ▼
POST /api/verification/employees/5/match (image)
       │
       ▼
matches_face_image() ✗ No Match
       │
       ├─► LoggingService.log_event(FACE_MISMATCH)
       │   - Log created: id=104
       │   - Image saved: static/logs/FACE_MISMATCH/FACE_MISMATCH_5_*.png
       │
       ▼
Response: {match: false, log_id: 104}
       │
       ▼
✗ SECURITY ALERT - Face doesn't match QR code!
```

## Database Table Relationships

```
┌──────────────────┐         ┌──────────────────┐
│   employees      │         │   event_logs     │
├──────────────────┤         ├──────────────────┤
│ id (PK)          │◄────────│ id (PK)          │
│ name             │         │ event_type       │
│ position         │         │ employee_id (FK) │
│ department       │         │ qr_code_hash     │
│ qr_code_hash     │         │ image_path       │
│ is_active        │         │ message          │
└──────────────────┘         │ timestamp        │
                             └──────────────────┘
```

## Event Type Decision Tree

```
                        ┌─────────────────┐
                        │  Event Occurs   │
                        └────────┬────────┘
                                 │
                    ┌────────────┼────────────┐
                    │                         │
              QR Code                    Face Image
              Scanned?                   Scanned?
                    │                         │
            ┌───────┴──────┐          ┌──────┴─────┐
            │              │          │            │
        Found?         Not Found?   Match?      Mismatch?
            │              │          │            │
            ├──►            │         ├──►          │
       QR_SCANNED      INVALID_QR    │      FACE_MISMATCH
            │              │         │            │
            └──────┬───────┘         └────┬───────┘
                   │                      │
            Can proceed to           LOG EVENT
            Face verification       (stored in DB)
                   │
              Face Match?
                   │
            ┌──────┴──────┐
            │             │
         Success      Failure
            │             │
            ├──►           └──►
   VERIFICATION_SUCCESS  FACE_MISMATCH
            │             │
         ✓ PASS          ✗ FAIL
```

## Image Storage Organization

```
static/logs/
│
├── INVALID_QR/
│   ├── INVALID_QR_20240115_143022_001.png
│   ├── INVALID_QR_20240115_143045_002.png
│   └── INVALID_QR_20240115_143110_003.png
│
├── FACE_MISMATCH/
│   ├── FACE_MISMATCH_5_20240115_143030_001.png    (employee_id_timestamp)
│   ├── FACE_MISMATCH_7_20240115_143100_002.png
│   └── FACE_MISMATCH_5_20240115_143200_003.png
│
├── VERIFICATION_SUCCESS/
│   ├── VERIFICATION_SUCCESS_5_20240115_143030_001.png
│   ├── VERIFICATION_SUCCESS_7_20240115_143100_002.png
│   └── VERIFICATION_SUCCESS_5_20240115_143200_003.png
│
├── QR_SCANNED/
│   ├── QR_SCANNED_5_20240115_143022_001.png
│   ├── QR_SCANNED_7_20240115_143045_002.png
│   └── QR_SCANNED_5_20240115_143110_003.png
│
└── FACE_SCANNED/
    ├── FACE_SCANNED_5_20240115_143030_001.png
    ├── FACE_SCANNED_7_20240115_143100_002.png
    └── FACE_SCANNED_5_20240115_143200_003.png
```

## API Response Summary

```
┌─────────────────────────────────────────────────────────────┐
│                    LOGGING API ENDPOINTS                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  GET /api/logs/                                            │
│  ├─ Returns: All logs with pagination                      │
│  └─ Use: Dashboard overview                                │
│                                                             │
│  GET /api/logs/type/{event_type}                           │
│  ├─ Returns: Logs filtered by event type                   │
│  └─ Use: Show only failed attempts, successful ones, etc.  │
│                                                             │
│  GET /api/logs/employee/{employee_id}                      │
│  ├─ Returns: All logs for specific employee               │
│  └─ Use: Employee activity history                         │
│                                                             │
│  GET /api/logs/date-range                                  │
│  ├─ Returns: Logs within date range                        │
│  └─ Use: Daily/weekly/monthly reports                      │
│                                                             │
│  GET /api/logs/statistics                                  │
│  ├─ Returns: Count of events by type                       │
│  └─ Use: Summary metrics                                   │
│                                                             │
│  GET /api/logs/event-types                                 │
│  ├─ Returns: Available event type names                    │
│  └─ Use: Build dropdown filters                            │
│                                                             │
│  GET /api/logs/image/{log_id}                              │
│  ├─ Returns: PNG image file                                │
│  └─ Use: View event photos                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Implementation Checklist

- ✅ Created EventLog database model
- ✅ Created LoggingService for business logic
- ✅ Created logging API endpoints
- ✅ Integrated with QR verification endpoint
- ✅ Integrated with face matching endpoint
- ✅ Registered logging blueprint
- ✅ Organized image storage by event type
- ✅ Added pagination support
- ✅ Added filtering by type, employee, date
- ✅ Added statistics endpoint
- ✅ Verified no syntax errors
- ✅ No breaking changes to existing code
