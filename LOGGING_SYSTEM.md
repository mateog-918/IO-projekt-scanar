# Event Logging System Documentation

## Overview

The event logging system automatically tracks all QR code scanning and face verification events in your application. Each event is stored in the database with:
- **Event Type**: Category of the event (QR_SCANNED, INVALID_QR, FACE_MISMATCH, VERIFICATION_SUCCESS)
- **Employee Information**: Which employee was involved (if applicable)
- **QR Code Hash**: The QR code that was scanned
- **Image Data**: Camera image associated with the event (optional, stored as files)
- **Timestamp**: When the event occurred
- **Message**: Additional context about the event

## Database Schema

### EventLog Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| event_type | String | Event category (see Event Types below) |
| employee_id | Integer | Foreign key to Employee table (nullable for invalid QR) |
| qr_code_hash | String | The QR code hash that was scanned |
| image_path | String | File path to stored image (nullable) |
| message | String | Additional info about the event |
| timestamp | DateTime | When the event occurred |
| created_at | DateTime | When the log entry was created |

## Event Types

1. **QR_SCANNED** - QR code was successfully scanned and found
2. **INVALID_QR** - QR code was scanned but not found in database
3. **FACE_SCANNED** - Face image was successfully scanned
4. **FACE_MISMATCH** - Face image doesn't match the employee's registered faces
5. **VERIFICATION_SUCCESS** - Complete successful verification (QR + face match)

## API Endpoints

### Get All Logs
```
GET /api/logs/
```
Returns all logs with pagination support.

**Query Parameters:**
- `limit`: Number of results per page (default: 100)
- `offset`: Number of results to skip (default: 0)

**Response:**
```json
{
  "success": true,
  "total": 250,
  "limit": 100,
  "offset": 0,
  "logs": [
    {
      "id": 1,
      "event_type": "VERIFICATION_SUCCESS",
      "employee_id": 5,
      "qr_code_hash": "abc123...",
      "image_path": "static/logs/VERIFICATION_SUCCESS/20240115_143022_123.png",
      "message": "Successful verification for employee John Doe",
      "timestamp": "2024-01-15T14:30:22.123000",
      "created_at": "2024-01-15T14:30:22.456000",
      "employee_name": "John Doe"
    }
  ]
}
```

### Get Logs by Event Type
```
GET /api/logs/type/{event_type}
```
Filter logs by specific event type.

**URL Parameters:**
- `event_type`: One of: INVALID_QR, FACE_MISMATCH, VERIFICATION_SUCCESS, QR_SCANNED, FACE_SCANNED

**Query Parameters:**
- `limit`: Number of results per page (default: 100)
- `offset`: Number of results to skip (default: 0)

**Example:**
```
GET /api/logs/type/INVALID_QR?limit=50&offset=0
```

### Get Logs by Employee
```
GET /api/logs/employee/{employee_id}
```
Get all logs for a specific employee.

**URL Parameters:**
- `employee_id`: Employee ID

**Query Parameters:**
- `limit`: Number of results per page (default: 100)
- `offset`: Number of results to skip (default: 0)

### Get Logs by Date Range
```
GET /api/logs/date-range
```
Retrieve logs within a specific date range.

**Query Parameters:**
- `start_date`: Start date (ISO format: 2024-01-01T00:00:00) - Required
- `end_date`: End date (ISO format: 2024-01-31T23:59:59) - Required
- `limit`: Number of results per page (default: 100)
- `offset`: Number of results to skip (default: 0)

**Example:**
```
GET /api/logs/date-range?start_date=2024-01-01T00:00:00&end_date=2024-01-15T23:59:59
```

### Get Event Statistics
```
GET /api/logs/statistics
```
Get count of events by type.

**Response:**
```json
{
  "success": true,
  "statistics": {
    "VERIFICATION_SUCCESS": 145,
    "INVALID_QR": 12,
    "FACE_MISMATCH": 8,
    "QR_SCANNED": 200,
    "total": 365
  }
}
```

### Get Event Types
```
GET /api/logs/event-types
```
Get list of all available event types.

**Response:**
```json
{
  "success": true,
  "event_types": [
    "INVALID_QR",
    "FACE_MISMATCH",
    "VERIFICATION_SUCCESS",
    "QR_SCANNED",
    "FACE_SCANNED"
  ]
}
```

### Get Log Image
```
GET /api/logs/image/{log_id}
```
Retrieve the image associated with a specific log entry.

**URL Parameters:**
- `log_id`: Event log ID

**Response:** PNG image file or error JSON

## Image Storage

Images are automatically saved to the `static/logs/` directory, organized by event type:

```
static/logs/
├── INVALID_QR/
│   ├── INVALID_QR_20240115_143022_123.png
│   └── INVALID_QR_20240115_143045_456.png
├── FACE_MISMATCH/
│   ├── FACE_MISMATCH_5_20240115_143030_789.png
│   └── ...
├── VERIFICATION_SUCCESS/
│   ├── VERIFICATION_SUCCESS_5_20240115_143040_012.png
│   └── ...
└── QR_SCANNED/
    └── ...
```

## Automatic Logging Integration

### QR Code Verification Endpoint

When you call `/api/verification/qr`, the system automatically logs:
- **Success**: Logs `QR_SCANNED` event with employee info
- **Failure**: Logs `INVALID_QR` event

**Updated Request Format:**
```json
{
  "qr_data": "hash_qr_kodu",
  "image": "base64_encoded_image_optional"
}
```

### Face Matching Endpoint

When you call `/api/verification/employees/{id}/match`, the system automatically logs:
- **Match**: Logs `VERIFICATION_SUCCESS` event with image
- **No Match**: Logs `FACE_MISMATCH` event with image

**Response now includes:**
```json
{
  "match": true/false,
  "log_id": 123
}
```

## Usage Examples

### Frontend Integration

**Get Recent Failed Verifications:**
```javascript
fetch('/api/logs/type/FACE_MISMATCH?limit=20')
  .then(r => r.json())
  .then(data => console.log(data.logs))
```

**Get Today's Events:**
```javascript
const today = new Date();
const start = today.toISOString().split('T')[0] + 'T00:00:00';
const end = today.toISOString().split('T')[0] + 'T23:59:59';

fetch(`/api/logs/date-range?start_date=${start}&end_date=${end}`)
  .then(r => r.json())
  .then(data => console.log(data.logs))
```

**Get Statistics:**
```javascript
fetch('/api/logs/statistics')
  .then(r => r.json())
  .then(data => {
    console.log(`Total events: ${data.statistics.total}`);
    console.log(`Invalid QRs: ${data.statistics.INVALID_QR}`);
    console.log(`Face mismatches: ${data.statistics.FACE_MISMATCH}`);
  })
```

**View Event Image:**
```javascript
// After getting a log entry with ID 123
const imageUrl = '/api/logs/image/123';
// Use in <img> tag or download
```

## Service Layer Usage (Backend)

The `LoggingService` class provides the following methods:

```python
from app.services.logging_service import LoggingService
from app.models.event_log import EventType

# Log an event
event_log = LoggingService.log_event(
    event_type=EventType.VERIFICATION_SUCCESS,
    employee_id=5,
    qr_code_hash="abc123",
    image_bytes=image_data,  # Optional
    message="Custom message"
)

# Get logs by type
logs, total = LoggingService.get_logs_by_type('INVALID_QR', limit=50)

# Get logs for employee
logs, total = LoggingService.get_logs_by_employee(employee_id=5)

# Get event statistics
stats = LoggingService.get_event_statistics()
```

## Database Initialization

The EventLog table is automatically created when the application starts (via `db.create_all()` in app.py).

## Filtering and Analysis

You can now create dashboards or reports that filter by:

1. **Event Type**: Show only invalid QR scans, face mismatches, or successful verifications
2. **Employee**: Track all events for a specific employee
3. **Time Period**: Analyze patterns over days, weeks, or months
4. **Statistics**: Get summary counts by event type

## Notes

- Images are saved as PNG files in `static/logs/` directory
- Image filenames include timestamp and event type for easy identification
- Image storage is optional - if no image is provided, the log is still created
- All timestamps are in UTC format (ISO 8601)
- Logs are immutable - use the ID to reference them but don't modify
- Database queries support pagination for large result sets
