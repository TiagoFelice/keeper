import asyncio
import gzip
import hashlib
import mimetypes
from typing import Any, AsyncIterator, Dict, Optional

from aioboto3 import Session as AsyncSession  # type: ignore

# from annotated_types import T  # type: ignore

PROFILE_NAME = "851725172192_DE"


class S3Service:
    def __init__(
        self,
        bucket_name: str,
    ):
        self.session = AsyncSession(profile_name=PROFILE_NAME)
        self.bucket_name = bucket_name

    async def save_file(self, key: str, value: bytes, **kwargs: Any) -> Dict[str, Any]:
        async with self.session.client("s3") as s3:
            etag: str | None = None
            try:
                response = await s3.head_object(Bucket=self.bucket_name, Key=key)
                etag = response["ETag"].strip('"')
            except Exception:
                pass

            if hashlib.md5(value).hexdigest() != etag:
                params = {
                    "Bucket": self.bucket_name,
                    "Key": key,
                    "Body": value,
                }

                if content_type := kwargs.get("content_type"):
                    params = {**params, "ContentType": content_type}
                    if extension := mimetypes.guess_extension(content_type):
                        params = {**params, "Key": f"{params['Key']}{extension}"}

                if kwargs.get("compress", False):
                    params = {
                        **params,
                        "Key": f"{params['Key']}.gz",
                        "Body": gzip.compress(value),
                        "ContentEncoding": "gzip",
                    }

                response = await s3.put_object(**params)
                return dict(response)
            return {"existing_key": key}

    async def get_file(self, key: str) -> Any:
        async with self.session.client("s3") as s3:
            response = await s3.get_object(Bucket=self.bucket_name, Key=key)
            return await response["Body"].read(), response["ContentType"]

    async def delete_file(self, key: str) -> None:
        async with self.session.client("s3") as s3:
            await s3.delete_object(Bucket=self.bucket_name, Key=key)

    # async def list(*, bucket: str, prefix: str, **kwargs) -> AsyncIterator[str]:
    #     session: AsyncSession = kwargs["aioboto3_session"]
    #     async with session.client("s3") as s3_client:
    #         paginator = s3_client.get_paginator("list_objects_v2")
    #         async for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
    #             for obj in page.get("Contents", []):
    #                 yield obj["Key"]
