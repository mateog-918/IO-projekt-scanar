"""
Employee Model Module
---------------------
This module defines the SQLAlchemy model for employees, storing biometric
and professional data.
"""

import io
import numpy as np
from PIL import Image
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Employee(db.Model):
    """
    Represents an employee in the system.
    
    This model handles the storage of personal details, professional roles, 
    and the biometric data (QR hashes and face encodings) required for 
    authentication.
    """
    __tablename__ = 'employees'

    #: Unique identifier for the employee
    id = db.Column(db.Integer, primary_key=True)

    #: Full name of the employee
    name = db.Column(db.String(100), nullable=False)

    #: Professional title (e.g., 'Software Engineer')
    position = db.Column(db.String(100))

    #: Company department name
    department = db.Column(db.String(100))

    #: Unique hash generated from the employee's QR code
    qr_code_hash = db.Column(db.String(255), unique=True, nullable=False)

    # Face Encodings (Binary Data)
    #: First face encoding (stored as binary float32 array)
    face_encoding_1 = db.Column(db.LargeBinary)
    #: Second face encoding (stored as binary float32 array)
    face_encoding_2 = db.Column(db.LargeBinary)
    #: Third face encoding (stored as binary float32 array)
    face_encoding_3 = db.Column(db.LargeBinary)
    #: Fourth face encoding (stored as binary float32 array)
    face_encoding_4 = db.Column(db.LargeBinary)
    #: Fifth face encoding (stored as binary float32 array)
    face_encoding_5 = db.Column(db.LargeBinary)

    # Face Image Paths
    #: Path to the first stored face image file
    face_image_path_1 = db.Column(db.String(255))
    #: Path to the second stored face image file
    face_image_path_2 = db.Column(db.String(255))
    #: Path to the third stored face image file
    face_image_path_3 = db.Column(db.String(255))
    #: Path to the fourth stored face image file
    face_image_path_4 = db.Column(db.String(255))
    #: Path to the fifth stored face image file
    face_image_path_5 = db.Column(db.String(255))

    #: Boolean flag indicating if the employee record is active
    is_active = db.Column(db.Boolean, default=True)

    #: The timestamp when the employee was added to the system
    created_at = db.Column(db.DateTime, default=db.func.now())

    def to_dict(self):
        """
        Convert the employee instance into a dictionary.

        Returns:
            dict: A dictionary containing the basic employee info and 
            a list of available image paths.
        """
        return {
            'id': self.id,
            'name': self.name,
            'position': self.position,
            'department': self.department,
            'qr_code_hash': self.qr_code_hash,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'face_image_paths': [p for p in (
                self.face_image_path_1, self.face_image_path_2, self.face_image_path_3,
                self.face_image_path_4, self.face_image_path_5) if p]
        }