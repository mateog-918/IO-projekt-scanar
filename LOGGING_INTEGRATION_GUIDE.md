# Event Logging System - Integration Guide

## Overview

Your QR code + face recognition factory access control system now includes a **complete event logging system** that tracks all verification attempts. This guide walks you through what was added and how to use it.

## What's New

### 1. Automatic Event Logging

Every access attempt is now logged automatically:
- ✅ QR code scans (valid and invalid)
- ✅ Face verification attempts (success and failure)
- ✅ Complete verification flows
- ✅ Associated images from the camera

### 2. New Database Table

An `event_logs` table has been created to store:
- Event type (INVALID_QR, FACE_MISMATCH, VERIFICATION_SUCCESS, etc.)
- Employee ID (if applicable)
- QR code hash
- Camera image path
- Timestamps and metadata

### 3. New API Endpoints

Seven new endpoints for accessing and analyzing logs:
- GET `/api/logs/` - All logs
- GET `/api/logs/type/{event_type}` - By event type
- GET `/api/logs/employee/{id}` - By employee
- GET `/api/logs/date-range` - By date range
- GET `/api/logs/statistics` - Summary stats
- GET `/api/logs/event-types` - Available types
- GET `/api/logs/image/{log_id}` - View images

## Getting Started

### Step 1: Restart the Flask Server

The system will automatically create the `event_logs` table on startup:

```bash
cd backend
python app.py
# or if using run script
# bash run.sh
```

### Step 2: Verify It's Working

Check that the logging system is active:

```bash
curl http://localhost:5000/api/logs/statistics
```

Expected response:
```json
{
  "success": true,
  "statistics": {
    "total": 0
  }
}
```

### Step 3: Run a Verification

Perform a normal QR + face verification through your app. This will create the first log entries.

### Step 4: Check Logs

```bash
curl http://localhost:5000/api/logs/
```

You should now see log entries for the verification you performed.

## Key Features

### 1. Event Filtering

Get only the logs you care about:

```bash
# All invalid QR scans
curl http://localhost:5000/api/logs/type/INVALID_QR

# All failed face matches
curl http://localhost:5000/api/logs/type/FACE_MISMATCH

# All successful verifications
curl http://localhost:5000/api/logs/type/VERIFICATION_SUCCESS

# All events for employee #5
curl http://localhost:5000/api/logs/employee/5

# Events from today
curl "http://localhost:5000/api/logs/date-range?start_date=2024-01-15T00:00:00&end_date=2024-01-15T23:59:59"
```

### 2. Statistics

Get overview of all events:

```bash
curl http://localhost:5000/api/logs/statistics
```

Response:
```json
{
  "success": true,
  "statistics": {
    "VERIFICATION_SUCCESS": 145,
    "FACE_MISMATCH": 8,
    "INVALID_QR": 12,
    "QR_SCANNED": 200,
    "total": 365
  }
}
```

### 3. Image Retrieval

View images associated with logs:

```bash
# Get a log entry first
curl http://localhost:5000/api/logs/ | jq '.logs[0].id'

# Download the image
curl http://localhost:5000/api/logs/image/101 --output event.png
```

## Event Types Reference

| Type | When Logged | Indicates |
|------|-----------|-----------|
| `QR_SCANNED` | Valid QR found | Employee authorized |
| `INVALID_QR` | QR not in DB | Invalid QR attempt |
| `FACE_MISMATCH` | Face doesn't match | Wrong person with valid QR |
| `VERIFICATION_SUCCESS` | Complete success | Person verified |

## Frontend Integration (Optional)

Your app works as-is, but you can enhance it:

### Send Images with QR Scan

```javascript
// Current code
fetch('/api/verification/qr', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ qr_data: scannedData })
})

// Enhanced code (with camera image)
const canvas = document.querySelector('canvas'); // Your camera canvas
const imageData = canvas.toDataURL('image/png');

fetch('/api/verification/qr', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    qr_data: scannedData,
    image: imageData  // NEW - optional
  })
})
```

### Add Logging Dashboard

```javascript
// Get today's statistics
async function getTodayStats() {
  const today = new Date().toISOString().split('T')[0];
  const response = await fetch(
    `/api/logs/date-range?` +
    `start_date=${today}T00:00:00&` +
    `end_date=${today}T23:59:59`
  );
  const data = await response.json();
  return data;
}

// Show failed attempts
async function showFailures() {
  const response = await fetch('/api/logs/type/FACE_MISMATCH?limit=20');
  const data = await response.json();
  console.log(`Failed face matches today: ${data.total}`);
  data.logs.forEach(log => {
    console.log(`- Employee ${log.employee_name}: ${log.timestamp}`);
  });
}

// View statistics
async function showStats() {
  const response = await fetch('/api/logs/statistics');
  const data = await response.json();
  console.log('Event Summary:');
  console.log(`Total events: ${data.statistics.total}`);
  console.log(`Successful verifications: ${data.statistics.VERIFICATION_SUCCESS}`);
  console.log(`Face mismatches: ${data.statistics.FACE_MISMATCH}`);
  console.log(`Invalid QRs: ${data.statistics.INVALID_QR}`);
}
```

## Database Structure

The new `event_logs` table:

```sql
event_logs (
  id: Integer (PK),
  event_type: String,           -- INVALID_QR, FACE_MISMATCH, etc.
  employee_id: Integer (FK),    -- Links to employees table
  qr_code_hash: String,         -- The QR code scanned
  image_path: String,           -- Path to saved image
  message: String,              -- Event description
  timestamp: DateTime,          -- When it happened
  created_at: DateTime          -- When logged
)
```

Related to `employees` table:
```
employees.id ←→ event_logs.employee_id
```

## Image Storage

Images are organized by event type in `static/logs/`:

```
static/logs/
├── INVALID_QR/
│   └── INVALID_QR_20240115_143022_001.png
├── FACE_MISMATCH/
│   └── FACE_MISMATCH_5_20240115_143030_001.png
├── VERIFICATION_SUCCESS/
│   └── VERIFICATION_SUCCESS_5_20240115_143040_001.png
└── QR_SCANNED/
    └── QR_SCANNED_5_20240115_143022_001.png
```

## Common Use Cases

### Monitor Access Attempts

```javascript
// Get all failed attempts in the last hour
const oneHourAgo = new Date(Date.now() - 60*60*1000).toISOString();
const now = new Date().toISOString();

fetch(`/api/logs/date-range?start_date=${oneHourAgo}&end_date=${now}`)
  .then(r => r.json())
  .then(data => {
    const failed = data.logs.filter(
      log => log.event_type === 'FACE_MISMATCH' || 
             log.event_type === 'INVALID_QR'
    );
    console.log(`Failed attempts: ${failed.length}`);
  });
```

### Generate Daily Report

```javascript
// Get report for a specific day
async function getDailyReport(date) {
  const start = `${date}T00:00:00`;
  const end = `${date}T23:59:59`;
  
  const response = await fetch(
    `/api/logs/date-range?start_date=${start}&end_date=${end}`
  );
  const data = await response.json();
  
  const stats = {};
  data.logs.forEach(log => {
    stats[log.event_type] = (stats[log.event_type] || 0) + 1;
  });
  
  console.log(`Report for ${date}:`);
  console.log(`- Total: ${data.total}`);
  console.log(`- Successful: ${stats.VERIFICATION_SUCCESS || 0}`);
  console.log(`- Face mismatches: ${stats.FACE_MISMATCH || 0}`);
  console.log(`- Invalid QRs: ${stats.INVALID_QR || 0}`);
}

getDailyReport('2024-01-15');
```

### Track Employee Activity

```javascript
// Get all events for an employee
async function getEmployeeActivity(employeeId) {
  const response = await fetch(`/api/logs/employee/${employeeId}?limit=100`);
  const data = await response.json();
  
  console.log(`Activity for employee #${employeeId}:`);
  console.log(`Total events: ${data.total}`);
  
  data.logs.forEach(log => {
    console.log(`[${log.timestamp}] ${log.event_type}`);
  });
}

getEmployeeActivity(5);
```

## Files Modified/Created

### New Files
- `backend/app/models/event_log.py` - Database model
- `backend/app/services/logging_service.py` - Service layer
- `backend/app/api/logging.py` - API endpoints

### Modified Files
- `backend/app.py` - Registered logging blueprint
- `backend/app/api/verification.py` - Integrated logging

### Documentation
- `LOGGING_SYSTEM.md` - Complete API documentation
- `LOGGING_QUICKSTART.md` - Quick start guide
- `LOGGING_API_EXAMPLES.md` - Request/response examples
- `LOGGING_ARCHITECTURE.md` - System architecture
- `LOGGING_IMPLEMENTATION.md` - Implementation details
- `LOGGING_CHECKLIST.md` - Implementation checklist

## Troubleshooting

### No logs appearing?
1. Restart Flask server
2. Check that `/api/logs/statistics` returns 200
3. Run a verification to create logs
4. Check response from `/api/logs/`

### Images not saving?
1. Ensure `static/logs/` directory exists and is writable
2. Check file permissions
3. Verify image is being sent in request

### Database errors?
1. Check that `event_log.py` is in `app/models/`
2. Verify imports in `app.py`
3. Check `instance/scanar.db` file permissions

## Performance Notes

- Pagination supported (default 100 items/page)
- Images stored as files, not in database
- Database queries are indexed
- Consider archiving logs periodically

## Security Notes

- All inputs validated
- File paths sanitized
- Image types checked
- Foreign key relationships enforced

## Next Steps

1. **Test it out** - Run some verifications and check logs
2. **Build dashboard** - Create a UI to view logs
3. **Generate reports** - Use APIs to create PDF/CSV reports
4. **Set up alerts** - Notify on suspicious activity
5. **Archive logs** - Clean up old logs periodically

## Need Help?

Refer to the detailed documentation:
- **Quick questions?** → [LOGGING_QUICKSTART.md](LOGGING_QUICKSTART.md)
- **API details?** → [LOGGING_SYSTEM.md](LOGGING_SYSTEM.md)
- **Example responses?** → [LOGGING_API_EXAMPLES.md](LOGGING_API_EXAMPLES.md)
- **Architecture?** → [LOGGING_ARCHITECTURE.md](LOGGING_ARCHITECTURE.md)
- **Implementation?** → [LOGGING_IMPLEMENTATION.md](LOGGING_IMPLEMENTATION.md)

---

**Ready to go!** 🚀 Your logging system is fully integrated and ready to track all access attempts.
