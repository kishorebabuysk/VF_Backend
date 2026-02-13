import os
from fastapi import UploadFile, HTTPException

ALLOWED_EXTENSIONS = {"pdf", "doc", "docx"}

def save_resume(file: UploadFile) -> str:
    ext = file.filename.split(".")[-1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid resume format")

    os.makedirs("uploads/resumes", exist_ok=True)

    file_path = f"uploads/resumes/{file.filename}"

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    return file_path
