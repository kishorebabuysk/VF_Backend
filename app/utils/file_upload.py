import os
import uuid
from fastapi import UploadFile

def save_upload_file(upload_dir: str, file: UploadFile) -> str:
    os.makedirs(upload_dir, exist_ok=True)

    filename = f"{uuid.uuid4()}_{file.filename}"
    path = os.path.join(upload_dir, filename)

    with open(path, "wb") as f:
        f.write(file.file.read())

    # return URL-safe path
    return path.replace("\\", "/")
