from __future__ import annotations

import io
from typing import TYPE_CHECKING, Literal

import aiotieba
import cv2
from fastapi.responses import StreamingResponse


from ..server import app

if TYPE_CHECKING:
    import numpy as np


class AnonymousAiotieba:
    _client: aiotieba.Client | None = None

    @classmethod
    async def client(cls):
        if not cls._client:
            cls._client = aiotieba.Client()
            await cls._client.__aenter__()
        return cls._client

    @classmethod
    async def stop(cls):
        if cls._client:
            await cls._client.__aexit__()
            cls._client = None


def ndarray2image(image: np.ndarray | None) -> io.BytesIO:
    if image is None or not image.any():
        image_bytes = b""
    else:
        image_bytes = cv2.imencode(".webp", image)[1].tobytes()

    return io.BytesIO(image_bytes)


@app.get("/resources/portrait/{portrait}", tags=["resources"])
async def get_portrait(
    portrait: str, size: Literal["s", "m", "l"] = "s"
) -> StreamingResponse:
    image = await (await AnonymousAiotieba.client()).get_portrait(portrait, size=size)
    return StreamingResponse(
        content=ndarray2image(image.img),
        media_type="image/webp",
        headers={"Cache-Control": "public, max-age=86400"},
    )


@app.get("/resources/image/{hash}", tags=["resources"])
async def get_image(hash: str, size: Literal["s", "m", "l"] = "s") -> StreamingResponse:  # noqa: A002
    image = await (await AnonymousAiotieba.client()).hash2image(hash, size=size)
    return StreamingResponse(
        content=ndarray2image(image.img),
        media_type="image/webp",
        headers={"Cache-Control": "public, max-age=86400"},
    )
