import os
from uuid import uuid4
from fastapi import UploadFile

UPLOAD_DIR = "uploads/csr"


def save_image(file: UploadFile) -> str:
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    ext = file.filename.split(".")[-1]
    filename = f"{uuid4().hex}.{ext}"
    path = os.path.join(UPLOAD_DIR, filename)

    with open(path, "wb") as buffer:
        buffer.write(file.file.read())

    return path.replace("\\", "/")