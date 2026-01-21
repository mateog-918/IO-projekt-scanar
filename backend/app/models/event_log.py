"""
Event Log Model Module
----------------------
This module defines the models for tracking and logging verification events,
including successful entries, face mismatches, and invalid QR scans.
"""

from datetime import datetime, timezone
from app.models.employee import db
from enum import Enum


class EventType(Enum):
    """
    Constants representing the different types of verification events 
    supported by the system.
    """
    #: The scanned QR code was not found in the database.
    INVALID_QR = "INVALID_QR"
    
    #: The QR code was valid, but the captured face did not match the employee.
    FACE_MISMATCH = "FACE_MISMATCH"
    
    #: Both QR and Face verification passed successfully.
    VERIFICATION_SUCCESS = "VERIFICATION_SUCCESS"
    
    #: A raw log indicating a QR code was successfully read.
    QR_SCANNED = "QR_SCANNED"
    
    #: A raw log indicating a face was successfully detected/scanned.
    FACE_SCANNED = "FACE_SCANNED"


class EventLog(db.Model):
    """
    Database model that stores a history of all verification attempts.
    
    This log acts as an audit trail for security, storing timestamps, 
    event types, and optional image data of the verification attempt.
    """
    __tablename__ = 'event_logs'

    #: Primary key for the log entry.
    id = db.Column(db.Integer, primary_key=True)

    #: The category of the event (maps to :class:`EventType`).
    event_type = db.Column(db.String(50), nullable=False)

    #: Foreign key linking to the :class:`Employee` (null if QR was invalid).
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)

    #: The raw hash of the QR code that was presented to the scanner.
    qr_code_hash = db.Column(db.String(255), nullable=True)

    #: Local filesystem path to the captured verification photo.
    image_path = db.Column(db.String(500), nullable=True)

    #: Binary blob of the captured image for direct database storage/retrieval.
    image_data = db.Column(db.LargeBinary, nullable=True)

    #: Human-readable details or error messages regarding the event.
    message = db.Column(db.Text, nullable=True)
    
    #: Snapshot of employee name at the time of the event (immutable log record).
    employee_name = db.Column(db.String(200), nullable=True)

    #: Timezone-aware UTC timestamp of when the event actually occurred.
    timestamp = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    #: Timezone-aware UTC timestamp of when this log entry was saved to the DB.
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    #: SQLAlchemy relationship linking the log back to the Employee model.
    employee = db.relationship('Employee', backref='events')

    def to_dict(self):
        """
        Serializes the log entry into a dictionary format.

        Handles timezone conversions to ensure all timestamps are 
        returned as UTC ISO-8601 strings.

        Returns:
            dict: A dictionary containing all log fields and the employee's name.
        """
        return {
            'id': self.id,
            'event_type': self.event_type,
            'employee_id': self.employee_id,
            'qr_code_hash': self.qr_code_hash,
            'image_path': self.image_path,
            'message': self.message,
            'timestamp': (
                self.timestamp.replace(tzinfo=timezone.utc) 
                if self.timestamp and self.timestamp.tzinfo is None 
                else self.timestamp
            ).astimezone(timezone.utc).isoformat() if self.timestamp else None,
            'created_at': (
                self.created_at.replace(tzinfo=timezone.utc) 
                if self.created_at and self.created_at.tzinfo is None 
                else self.created_at
            ).astimezone(timezone.utc).isoformat() if self.created_at else None,
            # Use stored snapshot, not dynamic relationship
            'employee_name': self.employee_name
        }