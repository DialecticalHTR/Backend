from dishka import Provider, provide, Scope

from src.domain.image import ImageRepository

from .repository import S3ImageRepository


class ImageProvider(Provider):
    image_repo = provide(
        provides=ImageRepository,
        source=S3ImageRepository,
        scope=Scope.REQUEST
    )
