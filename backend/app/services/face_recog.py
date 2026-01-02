"""Utilities for working with face encodings stored on Employee records.

This module centralizes encoding/decoding and matching logic so the
SQLAlchemy model remains focused on data structure only.
"""
from __future__ import annotations

import io
from typing import Optional

import numpy as np
from PIL import Image

from app.models.employee import Employee


def encode_to_bytes(vec: np.ndarray) -> bytes:
    return np.asarray(vec, dtype=np.float32).tobytes()


def decode_from_bytes(b: bytes) -> np.ndarray:
    return np.frombuffer(b, dtype=np.float32)


def get_face_encodings(emp: Employee) -> np.ndarray:
    encs = []
    for b in (
        emp.face_encoding_1,
        emp.face_encoding_2,
        emp.face_encoding_3,
        emp.face_encoding_4,
        emp.face_encoding_5,
    ):
        if b is not None:
            encs.append(decode_from_bytes(b))
    return np.stack(encs) if encs else np.empty((0,))


def count_face_encodings(emp: Employee) -> int:
    return get_face_encodings(emp).shape[0]


def add_face_encoding(emp: Employee, vec: np.ndarray, image_path: Optional[str] = None) -> bool:
    """Add a face encoding to the first available slot. Returns True on success."""
    b = encode_to_bytes(vec)
    slots = [
        "face_encoding_1",
        "face_encoding_2",
        "face_encoding_3",
        "face_encoding_4",
        "face_encoding_5",
    ]
    path_slots = [
        "face_image_path_1",
        "face_image_path_2",
        "face_image_path_3",
        "face_image_path_4",
        "face_image_path_5",
    ]
    for i, slot in enumerate(slots):
        if getattr(emp, slot) is None:
            setattr(emp, slot, b)
            if image_path:
                setattr(emp, path_slots[i], image_path)
            return True
    return False


def remove_face_encoding(emp: Employee, index: int) -> None:
    """Remove encoding at 1-based index (1..5)."""
    if 1 <= index <= 5:
        setattr(emp, f"face_encoding_{index}", None)
        setattr(emp, f"face_image_path_{index}", None)


def matches_embedding(emp: Employee, query_vec: np.ndarray, threshold: float = 0.6, metric: str = "euclidean") -> bool:
    """Compare a query embedding to stored encodings using euclidean or cosine distance."""
    encs = get_face_encodings(emp)
    if encs.shape[0] == 0:
        return False
    if metric == "euclidean":
        dists = np.linalg.norm(encs - query_vec, axis=1)
    elif metric == "cosine":
        qn = query_vec / np.linalg.norm(query_vec)
        en = encs / np.linalg.norm(encs, axis=1, keepdims=True)
        dists = 1.0 - (en @ qn)
    else:
        raise ValueError("unsupported metric")
    return np.min(dists) <= threshold


def matches_face_image(emp: Employee, image_bytes: bytes, tolerance: float = 0.6) -> bool:
    """Compute embedding from image bytes using face_recognition and compare to stored encodings."""
    try:
        import face_recognition
    except Exception as e:
        raise RuntimeError("face_recognition is required for image-based matching") from e

    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img_arr = np.array(img)
    encs = face_recognition.face_encodings(img_arr)
    if not encs:
        return False
    query_vec = encs[0]
    return matches_embedding(emp, query_vec, threshold=tolerance)
