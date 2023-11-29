from fastapi import UploadFile
from PIL import Image
from io import BytesIO


async def handle_images(images: list[UploadFile]) -> list[Image.Image]:
    resized_images = []

    for index, image in enumerate(images):
        pillow_img = Image.open(BytesIO(await image.read())).convert('RGB')

        if index == 0:
            resized_preview = await resize_preview(pillow_img)
            resized_images.append(resized_preview)

        resized_img = await resize(pillow_img)
        resized_images.append(resized_img)

    return resized_images


async def resize(img: Image.Image):
    if img.width <= 1600 and img.height <= 1600:
        return img

    w = 1600
    k = img.height / img.width
    resized_img = img.resize((w, int(w * k)))

    return resized_img


async def resize_preview(img: Image.Image) -> Image.Image:
    w = 308
    h = 385
    resampling = Image.Resampling.LANCZOS
    k = img.height / img.width
    resized_img = img.resize((w, int(w * k)), resampling)

    if resized_img.height < h:
        k = img.width / img.height
        resized_img = img.resize((int(h * k), h), resampling)

    if resized_img.height > h:
        resized_img = await crop_preview_height(resized_img)

    if resized_img.width > w:
        resized_img = await crop_preview_width(resized_img)

    return resized_img


async def crop_preview_height(img: Image.Image) -> Image.Image:
    h = 385
    x1, y1 = 0, (img.height - h) // 2
    x2, y2 = img.width, ((img.height - h) // 2) + h
    resized_img = img.crop((x1, y1, x2, y2))

    return resized_img


async def crop_preview_width(img: Image.Image) -> Image.Image:
    w = 308
    x1, y1 = (img.width - w) // 2, 0
    x2, y2 = ((img.width - w) // 2) + w, img.height
    resized_img = img.crop((x1, y1, x2, y2))

    return resized_img
