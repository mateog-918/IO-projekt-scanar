import io
import numpy as np
from PIL import Image
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def encode_to_bytes(vec: np.ndarray) -> bytes:
    return np.asarray(vec, dtype=np.float32).tobytes()


def decode_from_bytes(b: bytes) -> np.ndarray:
    return np.frombuffer(b, dtype=np.float32)


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

    def get_face_encodings(self) -> np.ndarray:
        encs = []
        for b in (self.face_encoding_1, self.face_encoding_2, self.face_encoding_3,
                  self.face_encoding_4, self.face_encoding_5):
            if b is not None:
                encs.append(decode_from_bytes(b))
        return np.stack(encs) if encs else np.empty((0,))

    def count_face_encodings(self) -> int:
        return self.get_face_encodings().shape[0]

    def add_face_encoding(self, vec: np.ndarray, image_path: str = None) -> bool:
        """Add a face encoding; returns True if added, False if already full (5)."""
        b = encode_to_bytes(vec)
        slots = ['face_encoding_1', 'face_encoding_2', 'face_encoding_3',
                 'face_encoding_4', 'face_encoding_5']
        path_slots = ['face_image_path_1', 'face_image_path_2', 'face_image_path_3',
                      'face_image_path_4', 'face_image_path_5']
        for i, slot in enumerate(slots):
            if getattr(self, slot) is None:
                setattr(self, slot, b)
                if image_path:
                    setattr(self, path_slots[i], image_path)
                return True
        return False

    def remove_face_encoding(self, index: int) -> None:
        """Remove encoding at 1-based index (1..5)."""
        if 1 <= index <= 5:
            setattr(self, f'face_encoding_{index}', None)
            setattr(self, f'face_image_path_{index}', None)

    def matches_embedding(self, query_vec: np.ndarray, threshold: float = 0.6, metric: str = 'euclidean') -> bool:
        """Compare a query embedding to stored encodings using euclidean or cosine distance."""
        encs = self.get_face_encodings()
        if encs.shape[0] == 0:
            return False
        if metric == 'euclidean':
            dists = np.linalg.norm(encs - query_vec, axis=1)
        elif metric == 'cosine':
            qn = query_vec / np.linalg.norm(query_vec)
            en = encs / np.linalg.norm(encs, axis=1, keepdims=True)
            dists = 1.0 - (en @ qn)
        else:
            raise ValueError('unsupported metric')
        return np.min(dists) <= threshold

    def matches_face_image(self, image_bytes: bytes, tolerance: float = 0.6) -> bool:
        """Compute embedding from image bytes using face_recognition and compare to stored encodings."""
        try:
            import face_recognition
        except Exception as e:
            raise RuntimeError('face_recognition is required for image-based matching') from e

        img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        img_arr = np.array(img)
        encs = face_recognition.face_encodings(img_arr)
        if not encs:
            return False
        query_vec = encs[0]
        return self.matches_embedding(query_vec, threshold=tolerance)

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