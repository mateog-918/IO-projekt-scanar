# Event Logging System - Quick Start Guide

## What Was Added

Your QR code and face recognition application now has a complete **event logging system** that tracks:

✅ **QR code scans** (valid and invalid)  
✅ **Face verification attempts** (matches and mismatches)  
✅ **Successful verifications** (complete flow)  
✅ **Associated images** from the camera for each event  
✅ **Event filtering and statistics**

## Files Created

### 1. Database Model
- **[app/models/event_log.py](backend/app/models/event_log.py)**
  - `EventLog` model with event_type, employee_id, image_path, timestamp, etc.
  - `EventType` enum with all event constants

### 2. Service Layer
- **[app/services/logging_service.py](backend/app/services/logging_service.py)**
  - `LoggingService` class with methods to:
    - Log events to database
    - Save images to disk
    - Retrieve logs by type, employee, or date range
    - Get event statistics

### 3. API Endpoints
- **[app/api/logging.py](backend/app/api/logging.py)**
  - RESTful endpoints for accessing and filtering logs
  - Endpoints to view images associated with logs
  - Statistics endpoint

### 4. Updated Files
- **[app.py](backend/app.py)** - Registered logging blueprint
- **[app/api/verification.py](backend/app/api/verification.py)** - Integrated logging into QR and face endpoints

## How to Use

### 1. Backend Automatically Logs Events

No changes needed to your frontend initially! The backend now automatically logs when:

```
QR Scan → /api/verification/qr → Logs QR_SCANNED or INVALID_QR
    ↓
Face Match → /api/verification/employees/{id}/match → Logs FACE_MISMATCH or VERIFICATION_SUCCESS
```

### 2. Frontend Can Send Camera Images (Optional)

Update your QR verification endpoint to include the camera image:

```javascript
// Old request
fetch('/api/verification/qr', {
  method: 'POST',
  body: JSON.stringify({ qr_data: scannedData })
})

// New request (with image)
fetch('/api/verification/qr', {
  method: 'POST',
  body: JSON.stringify({
    qr_data: scannedData,
    image: canvasElement.toDataURL('image/png') // base64 encoded
  })
})
```

### 3. View Logs via API

#### Get all events from today:
```bash
curl "http://localhost:5000/api/logs/date-range?start_date=2024-01-15T00:00:00&end_date=2024-01-15T23:59:59"
```

#### Get all invalid QR scans:
```bash
curl "http://localhost:5000/api/logs/type/INVALID_QR"
```

#### Get face mismatch events:
```bash
curl "http://localhost:5000/api/logs/type/FACE_MISMATCH"
```

#### Get all events for an employee:
```bash
curl "http://localhost:5000/api/logs/employee/5"
```

#### Get event statistics:
```bash
curl "http://localhost:5000/api/logs/statistics"
```

#### View an image from a log:
```bash
# Get the log ID first, then:
curl "http://localhost:5000/api/logs/image/123" --output image.png
```

## Event Types

| Event Type | When It Happens |
|------------|-----------------|
| `QR_SCANNED` | QR code is valid and found in database |
| `INVALID_QR` | QR code is scanned but not in database |
| `FACE_MISMATCH` | Face image doesn't match employee's faces |
| `VERIFICATION_SUCCESS` | Complete successful verification |
| `FACE_SCANNED` | Face image successfully captured |

## Build a Dashboard

The logging system is designed to support creating a comprehensive dashboard:

```javascript
// Example: Show today's verification success rate
async function getSuccessRate() {
  const today = new Date().toISOString().split('T')[0];
  const start = `${today}T00:00:00`;
  const end = `${today}T23:59:59`;
  
  const allLogs = await fetch(
    `/api/logs/date-range?start_date=${start}&end_date=${end}`
  ).then(r => r.json());
  
  const stats = await fetch('/api/logs/statistics').then(r => r.json());
  
  const total = stats.statistics.total;
  const success = stats.statistics.VERIFICATION_SUCCESS;
  const rate = (success / total * 100).toFixed(2);
  
  return { total, success, rate: `${rate}%` };
}
```

## Database Storage

- **Event logs**: Stored in `instance/scanar.db` (SQLite)
- **Images**: Stored in `static/logs/` organized by event type
- **Automatic cleanup**: Not implemented yet (you may want to add archival)

## Performance Considerations

- Pagination is supported on all endpoints (default: 100 per page)
- Images are stored as files, not in database
- Consider adding indexes on frequently queried fields (event_type, employee_id, timestamp)
- Archive old logs periodically to keep database performant

## Next Steps (Optional)

1. **Add Frontend Dashboard**
   - Display event statistics
   - Show recent logs filtered by type
   - Timeline view of events
   - Analytics/trends

2. **Add Alerts**
   - Notify when too many face mismatches occur
   - Alert on invalid QR attempts
   - Send reports

3. **Add Export**
   - CSV export of logs
   - Generate PDF reports

4. **Add Cleanup**
   - Automatic deletion of old logs
   - Archive logs to another storage

5. **Add Detailed Filtering**
   - Filter by multiple event types at once
   - Combined filters (employee + date range + type)

## Troubleshooting

**Q: Images aren't saving?**  
A: Check that `static/logs/` directory exists and is writable.

**Q: No logs appearing?**  
A: Make sure you restarted the Flask app after the changes.

**Q: Getting import errors?**  
A: The EventLog model needs to be imported before db.create_all() runs. This is handled in app.py.

## Database Reset

If you need to clear all logs:

```python
from app.models.event_log import EventLog
from app.models.employee import db

EventLog.query.delete()
db.session.commit()
```

---

For full API documentation, see [LOGGING_SYSTEM.md](LOGGING_SYSTEM.md)
