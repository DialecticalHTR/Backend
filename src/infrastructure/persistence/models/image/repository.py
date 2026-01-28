from io import BytesIO
from uuid import UUID

from types_boto3_s3 import S3ServiceResource

from src.domain.image import Image, ImageRepository

from src.infrastructure.persistence.technology.s3.url import S3Url


class S3ImageRepository(ImageRepository):
    def __init__(self, resource: S3ServiceResource):
        self.resource = resource

        bucket = S3Url("s3://images").get_bucket(self.resource)
        if bucket.creation_date is None:
            bucket.create()

    async def update(self, image: Image):
        obj = S3Url(f"s3://images/{image.id}").get_object(self.resource)
        
        with BytesIO(image.data) as data:
            obj.upload_fileobj(data)

    async def delete_by_id(self, image_id: UUID):
        obj = S3Url(f"s3://images/{image_id}").get_object(self.resource)
        obj.delete()

    async def get_by_id(self, image_id: UUID) -> Image:
        obj = S3Url(f"s3://images/{image_id}").get_object(self.resource)

        with BytesIO() as data:
            obj.download_fileobj(data)
            return Image(image_id, data.getvalue())
        