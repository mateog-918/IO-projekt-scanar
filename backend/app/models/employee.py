import io
import numpy as np
from PIL import Image
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# NOTE: Face recognition helper functions (encoding/decoding and matching)
# have been moved to `app.services.face_recog` to keep the model focused on data.


class Employee(db.Model):
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100))
    department = db.Column(db.String(100))
    qr_code_hash = db.Column(db.String(255), unique=True, nullable=False)

    # Up to 5 face encodings (binary float32) and optional image paths
    face_encoding_1 = db.Column(db.LargeBinary)
    face_encoding_2 = db.Column(db.LargeBinary)
    face_encoding_3 = db.Column(db.LargeBinary)
    face_encoding_4 = db.Column(db.LargeBinary)
    face_encoding_5 = db.Column(db.LargeBinary)

    face_image_path_1 = db.Column(db.String(255))
    face_image_path_2 = db.Column(db.String(255))
    face_image_path_3 = db.Column(db.String(255))
    face_image_path_4 = db.Column(db.String(255))
    face_image_path_5 = db.Column(db.String(255))

    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.now())

    # Face-recognition operations (get/add/remove/match encodings) moved to
    # `app.services.face_recog`. Use functions from that module (for example,
    # `from app.services.face_recog import add_face_encoding, count_face_encodings, matches_face_image`)
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'position': self.position,
            'qr_code_hash': self.qr_code_hash,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'face_image_paths': [p for p in (
                self.face_image_path_1, self.face_image_path_2, self.face_image_path_3,
                self.face_image_path_4, self.face_image_path_5) if p]
        }