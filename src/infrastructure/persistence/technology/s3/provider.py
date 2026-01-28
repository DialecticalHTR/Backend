import boto3
from types_boto3_s3 import S3ServiceResource
from dishka import Provider, provide, Scope


from .settings import S3Settings


class S3Provider(Provider):
    @provide(scope=Scope.APP)
    def provide_settings(self) -> S3Settings:
        return S3Settings() # type: ignore

    @provide(scope=Scope.REQUEST)
    def provide_resource(self, settings: S3Settings) -> S3ServiceResource:
        return boto3.resource(
            's3',
            aws_access_key_id=settings.access_key,
            aws_secret_access_key=settings.secret_key,
            aws_session_token=settings.session_token,
            endpoint_url=settings.endpoint_url,
            region_name=settings.region_name
        )
    
