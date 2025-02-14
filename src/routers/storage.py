import gzip
import os
from typing import Annotated, Any

from fastapi import APIRouter, Body, File, HTTPException, Path, Response, UploadFile

from src.services.s3_service import S3Service

router = APIRouter(prefix="/storage", tags=["Storage"])


# @router.post("/{bucket}/{key:path}")
# async def create_object(
#     bucket: str,
#     key: str = Path(..., min_length=1),
#     file: UploadFile = File(...),
#     compress: bool = False,
# ) -> Any:
#     if ".." in key:  # Prevent directory traversal
#         raise HTTPException(400, "Invalid key")
#     s3 = S3Service(bucket)
#     content = await file.read()
#     result = await s3.save_file(
#         key=key,
#         value=content,
#         content_type=file.content_type,
#         compress=compress,
#     )
#     if "existing_key" in result:
#         raise HTTPException(
#             409, f"Duplicate content exists at {result['existing_key']}"
#         )
#     return result["ETag"].strip('"')

@router.post("")
async def create(key: Annotated[str, Body()], value: Annotated[dict[str, Any], Body()]) -> Any:
    return {"key": key, "value": value}


@router.get("/{key:path}")
async def get_object(bucket: str, key: str) -> Response:
    s3 = S3Service(bucket)
    content, media_type = await s3.get_file(key)

    filename, ext = os.path.splitext(key)
    if ext == ".gz":
        content = gzip.decompress(content)
        key = filename  # Remove the .gz extension for the filename

    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={key}"},
    )


@router.delete("/{key:path}")
async def delete_object(bucket: str, key: str) -> Response:
    s3 = S3Service(bucket)
    await s3.delete_file(key)
    return Response(status_code=204, content="Successfully deleted")
