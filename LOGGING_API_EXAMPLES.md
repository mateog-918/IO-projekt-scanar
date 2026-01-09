# Event Logging API - Response Examples

## 1. QR Code Verification - VALID QR

**Request:**
```bash
curl -X POST http://localhost:5000/api/verification/qr \
  -H "Content-Type: application/json" \
  -d '{
    "qr_data": "abc123hash",
    "image": "data:image/png;base64,iVBORw0KGgo..."
  }'
```

**Response (200):**
```json
{
  "success": true,
  "message": "Witaj, Jan Kowalski",
  "employee": {
    "id": 5,
    "name": "Jan Kowalski",
    "position": "Engineer",
    "department": "IT",
    "qr_code_hash": "abc123hash",
    "is_active": true,
    "created_at": "2024-01-10T10:30:00.000000"
  }
}
```

**Log Created:**
```json
{
  "id": 101,
  "event_type": "QR_SCANNED",
  "employee_id": 5,
  "qr_code_hash": "abc123hash",
  "image_path": "static/logs/QR_SCANNED/QR_SCANNED_5_20240115_143022_123.png",
  "message": "QR code successfully scanned for Jan Kowalski",
  "timestamp": "2024-01-15T14:30:22.123000",
  "created_at": "2024-01-15T14:30:22.456000",
  "employee_name": "Jan Kowalski"
}
```

---

## 2. QR Code Verification - INVALID QR

**Request:**
```bash
curl -X POST http://localhost:5000/api/verification/qr \
  -H "Content-Type: application/json" \
  -d '{
    "qr_data": "invalid_hash_xyz"
  }'
```

**Response (404):**
```json
{
  "success": false,
  "message": "Nie znaleziono pracownika dla podanego QR kodu",
  "employee": null
}
```

**Log Created:**
```json
{
  "id": 102,
  "event_type": "INVALID_QR",
  "employee_id": null,
  "qr_code_hash": "invalid_hash_xyz",
  "image_path": null,
  "message": "Invalid QR code scanned",
  "timestamp": "2024-01-15T14:31:45.789000",
  "created_at": "2024-01-15T14:31:45.890000",
  "employee_name": null
}
```

---

## 3. Face Verification - MATCH (Success)

**Request:**
```bash
curl -X POST http://localhost:5000/api/verification/employees/5/match \
  -F "image=@photo.png"
```

**Response (200):**
```json
{
  "match": true,
  "log_id": 103
}
```

**Log Created:**
```json
{
  "id": 103,
  "event_type": "VERIFICATION_SUCCESS",
  "employee_id": 5,
  "qr_code_hash": null,
  "image_path": "static/logs/VERIFICATION_SUCCESS/VERIFICATION_SUCCESS_5_20240115_143030_456.png",
  "message": "Successful verification for employee Jan Kowalski",
  "timestamp": "2024-01-15T14:30:30.456000",
  "created_at": "2024-01-15T14:30:30.890000",
  "employee_name": "Jan Kowalski"
}
```

---

## 4. Face Verification - NO MATCH (Failure)

**Request:**
```bash
curl -X POST http://localhost:5000/api/verification/employees/5/match \
  -F "image=@wrong_person.png"
```

**Response (200):**
```json
{
  "match": false,
  "log_id": 104
}
```

**Log Created:**
```json
{
  "id": 104,
  "event_type": "FACE_MISMATCH",
  "employee_id": 5,
  "qr_code_hash": null,
  "image_path": "static/logs/FACE_MISMATCH/FACE_MISMATCH_5_20240115_143040_789.png",
  "message": "Face mismatch for employee Jan Kowalski",
  "timestamp": "2024-01-15T14:30:40.789000",
  "created_at": "2024-01-15T14:30:40.890000",
  "employee_name": "Jan Kowalski"
}
```

---

## 5. Get All Logs

**Request:**
```bash
curl "http://localhost:5000/api/logs/?limit=10&offset=0"
```

**Response (200):**
```json
{
  "success": true,
  "total": 250,
  "limit": 10,
  "offset": 0,
  "logs": [
    {
      "id": 104,
      "event_type": "FACE_MISMATCH",
      "employee_id": 5,
      "qr_code_hash": null,
      "image_path": "static/logs/FACE_MISMATCH/FACE_MISMATCH_5_20240115_143040_789.png",
      "message": "Face mismatch for employee Jan Kowalski",
      "timestamp": "2024-01-15T14:30:40.789000",
      "created_at": "2024-01-15T14:30:40.890000",
      "employee_name": "Jan Kowalski"
    },
    {
      "id": 103,
      "event_type": "VERIFICATION_SUCCESS",
      "employee_id": 5,
      "qr_code_hash": null,
      "image_path": "static/logs/VERIFICATION_SUCCESS/VERIFICATION_SUCCESS_5_20240115_143030_456.png",
      "message": "Successful verification for employee Jan Kowalski",
      "timestamp": "2024-01-15T14:30:30.456000",
      "created_at": "2024-01-15T14:30:30.890000",
      "employee_name": "Jan Kowalski"
    }
  ]
}
```

---

## 6. Get Logs by Event Type

**Request:**
```bash
curl "http://localhost:5000/api/logs/type/INVALID_QR?limit=50"
```

**Response (200):**
```json
{
  "success": true,
  "event_type": "INVALID_QR",
  "total": 12,
  "limit": 50,
  "offset": 0,
  "logs": [
    {
      "id": 102,
      "event_type": "INVALID_QR",
      "employee_id": null,
      "qr_code_hash": "invalid_hash_xyz",
      "image_path": null,
      "message": "Invalid QR code scanned",
      "timestamp": "2024-01-15T14:31:45.789000",
      "created_at": "2024-01-15T14:31:45.890000",
      "employee_name": null
    }
  ]
}
```

---

## 7. Get Logs by Employee

**Request:**
```bash
curl "http://localhost:5000/api/logs/employee/5?limit=100"
```

**Response (200):**
```json
{
  "success": true,
  "employee_id": 5,
  "total": 45,
  "limit": 100,
  "offset": 0,
  "logs": [
    {
      "id": 104,
      "event_type": "FACE_MISMATCH",
      "employee_id": 5,
      "qr_code_hash": null,
      "image_path": "static/logs/FACE_MISMATCH/FACE_MISMATCH_5_20240115_143040_789.png",
      "message": "Face mismatch for employee Jan Kowalski",
      "timestamp": "2024-01-15T14:30:40.789000",
      "created_at": "2024-01-15T14:30:40.890000",
      "employee_name": "Jan Kowalski"
    }
  ]
}
```

---

## 8. Get Logs by Date Range

**Request:**
```bash
curl "http://localhost:5000/api/logs/date-range?start_date=2024-01-15T00:00:00&end_date=2024-01-15T23:59:59&limit=100"
```

**Response (200):**
```json
{
  "success": true,
  "start_date": "2024-01-15T00:00:00",
  "end_date": "2024-01-15T23:59:59",
  "total": 35,
  "limit": 100,
  "offset": 0,
  "logs": [
    {
      "id": 104,
      "event_type": "FACE_MISMATCH",
      "employee_id": 5,
      "qr_code_hash": null,
      "image_path": "static/logs/FACE_MISMATCH/FACE_MISMATCH_5_20240115_143040_789.png",
      "message": "Face mismatch for employee Jan Kowalski",
      "timestamp": "2024-01-15T14:30:40.789000",
      "created_at": "2024-01-15T14:30:40.890000",
      "employee_name": "Jan Kowalski"
    }
  ]
}
```

---

## 9. Get Event Statistics

**Request:**
```bash
curl "http://localhost:5000/api/logs/statistics"
```

**Response (200):**
```json
{
  "success": true,
  "statistics": {
    "VERIFICATION_SUCCESS": 145,
    "FACE_MISMATCH": 8,
    "INVALID_QR": 12,
    "QR_SCANNED": 200,
    "FACE_SCANNED": 150,
    "total": 515
  }
}
```

---

## 10. Get Available Event Types

**Request:**
```bash
curl "http://localhost:5000/api/logs/event-types"
```

**Response (200):**
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

---

## 11. Download Image from Log

**Request:**
```bash
curl "http://localhost:5000/api/logs/image/103" --output verification_image.png
```

**Response:** PNG image file (binary)

**Error Response (image not found):**
```json
{
  "success": false,
  "error": "No image associated with this log"
}
```

---

## Error Responses

### Invalid Date Format
**Request:**
```bash
curl "http://localhost:5000/api/logs/date-range?start_date=invalid&end_date=2024-01-15"
```

**Response (400):**
```json
{
  "success": false,
  "error": "Invalid date format: time data 'invalid' does not match any format"
}
```

### Missing Required Parameters
**Request:**
```bash
curl "http://localhost:5000/api/logs/date-range"
```

**Response (400):**
```json
{
  "success": false,
  "error": "start_date and end_date parameters are required (ISO format)"
}
```

### Server Error
**Response (500):**
```json
{
  "success": false,
  "error": "Internal server error description"
}
```

---

## Frontend Usage Example

```javascript
// Fetch logs from the last 24 hours
async function getLast24HoursLogs() {
  const now = new Date();
  const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);
  
  const startDate = yesterday.toISOString();
  const endDate = now.toISOString();
  
  const response = await fetch(
    `/api/logs/date-range?start_date=${startDate}&end_date=${endDate}`
  );
  const data = await response.json();
  return data.logs;
}

// Get all failed verifications
async function getFailedVerifications() {
  const response = await fetch('/api/logs/type/FACE_MISMATCH');
  const data = await response.json();
  return data.logs;
}

// Get statistics
async function showStats() {
  const response = await fetch('/api/logs/statistics');
  const data = await response.json();
  console.log(`Total verifications: ${data.statistics.total}`);
  console.log(`Successful: ${data.statistics.VERIFICATION_SUCCESS}`);
  console.log(`Failed: ${data.statistics.FACE_MISMATCH}`);
  console.log(`Invalid QR: ${data.statistics.INVALID_QR}`);
}

// Display image from log
async function displayLogImage(logId) {
  const imageUrl = `/api/logs/image/${logId}`;
  const img = document.createElement('img');
  img.src = imageUrl;
  document.body.appendChild(img);
}
```
