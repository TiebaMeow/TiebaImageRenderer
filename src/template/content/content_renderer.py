from typing import List
from pathlib import Path
from fastapi import Response
from pydantic import BaseModel


from src.renderer import renderer, RenderParam
from src.api.server import app


class User(BaseModel):
    username: str
    portrait: str
    level: int


class ContentData(BaseModel):
    title: str
    text: str
    images: List[str]
    user: User
    create_time: int
    prefix: str | None = None
    suffix: str | None = None


class ContentRenderRequest(RenderParam):
    data: ContentData
    width: int | None = 550 # w


@app.post("/renderer/content")
async def render_content(request: ContentRenderRequest):
    # Resolve template path relative to this file
    # This file is in src/template/content/
    # template.html is in src/template/

    screenshot, is_complete = await renderer.render(
        Path(__file__).parent / "template.html", request
    )

    headers = {"complete": "true" if is_complete else "false"}

    return Response(content=screenshot, media_type="image/jpeg", headers=headers)
