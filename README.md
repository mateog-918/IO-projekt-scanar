# SCANAR - Access Control System

**Employee access verification system using QR codes and face recognition**

Software Engineering university project

---

## Table of Contents
- [About](#about)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Documentation](#documentation)
- [System Architecture](#system-architecture)
- [Authors](#authors)

---

## About

SCANAR is an access control solution designed for industrial companies managing large work facilities. The system addresses security concerns related to access card sharing between employees through a robust two-stage verification process.

### Problem Statement

Traditional magnetic card systems are vulnerable to abuse where employees share access cards, resulting in:
- Inaccurate time tracking
- False work reports
- Compromised facility security
- Unreliable access logs

### Solution

SCANAR implements a dual-verification system that combines:

1. **QR Code Scanning** - Each employee receives a unique QR code pass
2. **Face Recognition** - Biometric identity verification using computer vision
3. **Event Logging** - Comprehensive audit trail of all access attempts
4. **Analytics & Reporting** - Real-time statistics and abuse detection


---

## Key Features

### Admin Panel
- Complete employee lifecycle management (Create, Read, Update, Delete)
- Unique QR code generation and distribution
- Face photo management (up to 5 photos per employee)
- Employee status control (activation/deactivation)
- Soft delete (deactivation) and hard delete options
- Profile editing (name, position, department)
- Individual face photo removal

### Verification System
- Real-time QR code validation
- Face matching against database of encodings
- Two-factor verification (QR + Face)
- Live camera feed integration
- Automatic event logging with timestamps
- Captured image storage for audit purposes

### Logs and Reporting
- Comprehensive event logging system
- Filter by event type (success, failure, invalid QR, face mismatch)
- Filter by employee
- Date range filtering
- Aggregated statistics dashboard
- Image capture for each verification attempt
- Export capabilities

### Authentication & Security
- Session-based admin authentication
- Protected management endpoints
- Configurable access control
- Default credentials: `admin` / `admin123`

---

## Technology Stack

### Backend
- **Flask 3.0.0** - Python web framework
- **SQLAlchemy 3.1.1** - ORM for database operations
- **SQLite** - Embedded database (development)
- **Flasgger 0.9.7.1** - Swagger/OpenAPI documentation
- **face_recognition** - Face detection and recognition library
- **opencv-python** - Computer vision and image processing
- **qrcode** - QR code generation
- **Pillow** - Image manipulation
- **Flask-CORS** - Cross-origin resource sharing

### Frontend
- **React 19.2.0** - UI library
- **Vite 6.0.5** - Build tool and dev server
- **React Router 7.1.3** - Client-side routing
- **jspdf + jspdf-autotable** - PDF report generation


---

## Documentation

Comprehensive documentation is available:

| Document | Description |
|----------|-------------|
| [Setup Instructions](Setup.md) | Complete installation and running guide |
| [Documentation Hub](Documentation.md) | Central documentation index |
| [Requirements Documentation (DIW)](docs/DIW.pdf) | Requirements engineering specification (Polish) |
| [Test Report](docs/Tests.pdf) | Software testing report (Polish) |
| [Code Documentation](docs/Code_Documentation.md) | Auto-generated code documentation (Sphinx) |
| [API Documentation](docs/API_Documentation.md) | Interactive API documentation (Swagger UI) |
| [Database Documentation](docs/Database_Documentation.md) | Database schema, file storage, and data management |


---

## System Architecture

```
┌─────────────────┐
│  React Frontend │ ← User Interface (Admin & Verification)
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐
│  Flask Backend  │ ← API Server + Business Logic
└────────┬────────┘
         │
    ┌────┴────┬────────────┬──────────────┐
    ▼         ▼            ▼              ▼
┌────────┐ ┌──────┐ ┌────────────┐ ┌─────────┐
│ SQLite │ │ QR   │ │ Face       │ │ Logging │
│   DB   │ │ Gen  │ │ Recognition│ │ Service │
└────────┘ └──────┘ └────────────┘ └─────────┘
```

**Database Schema:**
- `employees` - Employee records with QR hashes and face encodings
- `event_logs` - Access attempt logs with timestamps and results

**File Storage:**
- `static/qr_codes/` - Generated QR code images
- `static/face_images/` - Employee face photos
- `static/logs/` - Verification attempt captures

---

## Authors

- [Mateusz Gacek](https://github.com/mateog-918)
- [Jan Ogiegło](https://github.com/Janosik8)
- [Paweł Kowalcze](https://github.com/PawelKowalcze)

**University**: AGH University of Krakow  
**Academic Year**: 2025/2026

---

## License

This project is an academic assignment for educational purposes.

---

## Acknowledgments

Built as part of Software Engineering course requirements.  
