import boto3
from PIL import Image
from io import BytesIO

from src.config import config


async def _get_aws_session() -> boto3.Session:
    aws_session = boto3.Session(
        aws_access_key_id=config.YOS_KEY_ID,
        aws_secret_access_key=config.YOS_SECRET_KEY,
        region_name='ru-central1',
    )

    return aws_session


async def _get_aws_client():
    aws_session = await _get_aws_session()
    aws_client = aws_session.client('s3', endpoint_url='https://storage.yandexcloud.net')

    return aws_client


async def upload_images(lot_id: int, images: list[Image.Image]):
    aws_client = await _get_aws_client()
    img_links = []
    src_prefix = f'https://storage.yandexcloud.net/{config.YOS_BUCKET}/'

    for index, img in enumerate(images):
        img_links.append(src_prefix + str(lot_id) + '/' + str(index) + '.jpg')
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG')
        aws_client.upload_fileobj(
            BytesIO(img_bytes.getvalue()),
            config.YOS_BUCKET,
            f'{lot_id}/{index}.jpg',
        )

    return img_links
