"""
Event Log model for tracking verification events
"""
from datetime import datetime, timezone
from app.models.employee import db
from enum import Enum


class EventType(Enum):
    """Event type constants"""
    INVALID_QR = "INVALID_QR"  # QR code not found in database
    FACE_MISMATCH = "FACE_MISMATCH"  # Face doesn't match the QR code's employee
    VERIFICATION_SUCCESS = "VERIFICATION_SUCCESS"  # Successful verification (QR + face match)
    QR_SCANNED = "QR_SCANNED"  # QR code successfully scanned
    FACE_SCANNED = "FACE_SCANNED"  # Face successfully scanned


class EventLog(db.Model):
    """
    EventLog model to store all verification events
    """
    __tablename__ = 'event_logs'

    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), nullable=False)  # INVALID_QR, FACE_MISMATCH, VERIFICATION_SUCCESS, etc.
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)  # Null if QR is invalid
    qr_code_hash = db.Column(db.String(255), nullable=True)  # The QR code that was scanned
    image_path = db.Column(db.String(500), nullable=True)  # Path to the image from the camera (if taken)
    image_data = db.Column(db.LargeBinary, nullable=True)  # Binary image data (optional, for direct retrieval)
    message = db.Column(db.Text, nullable=True)  # Additional info about the event
    # Use timezone-aware UTC timestamps
    # Use timezone-aware UTC timestamps and store timezone information in the DB column
    timestamp = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationship to employee (optional)
    employee = db.relationship('Employee', backref='events')

    def to_dict(self):
        """Convert event log to dictionary"""
        return {
            'id': self.id,
            'event_type': self.event_type,
            'employee_id': self.employee_id,
            'qr_code_hash': self.qr_code_hash,
            'image_path': self.image_path,
            'message': self.message,
            # Ensure we serialize timezone-aware ISO strings. If datetime is naive, assume UTC.
            'timestamp': (self.timestamp.replace(tzinfo=timezone.utc) if self.timestamp and self.timestamp.tzinfo is None else self.timestamp).astimezone(timezone.utc).isoformat() if self.timestamp else None,
            'created_at': (self.created_at.replace(tzinfo=timezone.utc) if self.created_at and self.created_at.tzinfo is None else self.created_at).astimezone(timezone.utc).isoformat() if self.created_at else None,
            'employee_name': self.employee.name if self.employee else None
        }
