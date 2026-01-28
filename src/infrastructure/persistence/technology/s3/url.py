import re

from types_boto3_s3 import S3ServiceResource
from types_boto3_s3.service_resource import Bucket, Object


ALLOWED_SYMBOLS = r"\.\-a-z0-9"
S3_URL_PATTERN = rf"^s3://(?P<bucket>[{ALLOWED_SYMBOLS}]+)(?:\/(?P<prefix>[{ALLOWED_SYMBOLS}/]*?)?)?$"

class S3Url:
    def __init__(self, url: str):
        if (match := re.match(S3_URL_PATTERN, url)) is None:
            raise ValueError("Url is not s3")
        
        self.bucket = match.group("bucket")
        self.prefix = match.group("prefix") or ""

    def __truediv__(self, to_append: str) -> "S3Url":
        # jank
        return S3Url(
            f"s3://{self.bucket}/{'' if not self.prefix else self.prefix + '/'}{to_append}"
    )

    @staticmethod
    def is_s3_url(url: str) -> bool:
        return re.match(S3_URL_PATTERN, url) is not None
    
    def get_bucket(self, resourse: S3ServiceResource) -> Bucket:
        return resourse.Bucket(self.bucket)
    
    def get_object(self, resource: S3ServiceResource) -> Object:
        return resource.Object(self.bucket, self.prefix)
    