"""
Face Recognition Service
------------------------
This module provides utility functions for handling face encodings, including
conversion between binary storage and NumPy arrays, and logic for matching 
embeddings against stored employee data.
"""

from __future__ import annotations

import io
from typing import Optional

import numpy as np
from PIL import Image

from app.models.employee import Employee


def encode_to_bytes(vec: np.ndarray) -> bytes:
    """
    Converts a NumPy encoding vector into a binary format for database storage.

    Args:
        vec (np.ndarray): The face encoding vector (usually 128 or 1024 dimensions).

    Returns:
        bytes: The float32 representation of the vector in bytes.
    """
    return np.asarray(vec, dtype=np.float32).tobytes()


def decode_from_bytes(b: bytes) -> np.ndarray:
    """
    Converts binary data from the database back into a NumPy array.

    Args:
        b (bytes): The binary float32 data.

    Returns:
        np.ndarray: The reconstructed face encoding vector.
    """
    return np.frombuffer(b, dtype=np.float32)


def get_face_encodings(emp: Employee) -> np.ndarray:
    """
    Retrieves all available face encodings for a given employee.

    Scans all five potential encoding slots in the Employee model and 
    decodes any that are not null.

    Args:
        emp (Employee): The employee instance to scan.

    Returns:
        np.ndarray: A 2D array of shape (N, D) where N is the number of encodings 
        found and D is the vector dimension. Returns an empty array if none found.
    """
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
    """
    Counts how many face encoding slots are currently filled for an employee.

    Args:
        emp (Employee): The employee instance.

    Returns:
        int: Number of stored encodings (0 to 5).
    """
    return get_face_encodings(emp).shape[0]


def add_face_encoding(emp: Employee, vec: np.ndarray, image_path: Optional[str] = None) -> bool:
    """
    Adds a new face encoding to the first available slot (1-5).

    Args:
        emp (Employee): The employee instance to update.
        vec (np.ndarray): The new face encoding vector.
        image_path (Optional[str]): filesystem path to the source image.

    Returns:
        bool: True if the encoding was added, False if all slots were full.
    """
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
    """
    Removes the face encoding and associated image path at a specific slot.

    Args:
        emp (Employee): The employee instance.
        index (int): The slot index to clear (1-based, 1 to 5).
    """
    if 1 <= index <= 5:
        setattr(emp, f"face_encoding_{index}", None)
        setattr(emp, f"face_image_path_{index}", None)


def matches_embedding(emp: Employee, query_vec: np.ndarray, threshold: float = 0.6, metric: str = "euclidean") -> bool:
    """
    Compares a new face embedding against all stored encodings for an employee.

    Args:
        emp (Employee): The employee to verify against.
        query_vec (np.ndarray): The encoding vector from the camera.
        threshold (float): The maximum distance to consider a 'match'. 
            Lower is stricter. Defaults to 0.6.
        metric (str): The distance calculation method ('euclidean' or 'cosine').

    Returns:
        bool: True if any stored encoding is within the threshold distance.

    Raises:
        ValueError: If an unsupported metric is provided.
    """
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
    """
    Processes a raw image and checks if it matches the stored employee encodings.

    This is a high-level wrapper that performs face detection and encoding
    extraction before calling :func:`matches_embedding`.

    Args:
        emp (Employee): The employee to verify.
        image_bytes (bytes): Raw bytes of the image (e.g., from a request).
        tolerance (float): Matching strictness. Defaults to 0.6.

    Returns:
        bool: True if a face is detected and matches.

    Raises:
        RuntimeError: If the `face_recognition` library is not installed.
    """
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