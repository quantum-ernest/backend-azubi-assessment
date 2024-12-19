import shutil
import uuid

from fastapi import HTTPException, UploadFile, status


def save_file(file: UploadFile | None = None) -> str:
    """
    Save an uploaded file to the server's local storage.

    This function saves an uploaded file to the `assets/images` directory,
    ensuring the file is of a valid type (JPEG, PNG, GIF). The saved file
    is assigned a unique name to avoid conflicts.

    Args:
        file (UploadFile | None): The uploaded file to save. Defaults to None.

    Returns:
        str: The name of the saved file. Returns None if no file is provided.

    Raises:
        HTTPException: If the file type is invalid.
    """
    if file:
        if file.content_type not in ["image/jpeg", "image/png", "image/gif"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file type"
            )
        filename = f"{uuid.uuid4()}_{file.filename.replace(' ', '')}"
        file_path = f"assets/images/{filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    else:
        filename = None
    return filename
