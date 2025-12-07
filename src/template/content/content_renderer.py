from typing import List
from pathlib import Path
from io import BytesIO
from datetime import datetime
from fastapi import Response
from pydantic import BaseModel
from jinja2 import Template
from weasyprint import HTML, CSS
from pdf2image import convert_from_bytes
from PIL import Image


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


class ContentRenderRequest(BaseModel):
    data: ContentData
    width: int | None = 550 # w
    host: str = "http://localhost:39334"


# Load template once at module startup
_TEMPLATE_PATH = Path(__file__).parent / "template_weasyprint.html"
with open(_TEMPLATE_PATH, "r", encoding="utf-8") as f:
    _TEMPLATE = Template(f.read())


def format_create_time(unix_timestamp: int) -> str:
    """Format Unix timestamp to Chinese date format."""
    dt = datetime.fromtimestamp(unix_timestamp)
    return f"{dt.month}月{dt.day}日 {dt.hour:02d}:{dt.minute:02d}"


@app.post("/renderer/content")
def render_content(request: ContentRenderRequest):
    # Format the create_time
    create_time_formatted = format_create_time(request.data.create_time)
    
    # Render the HTML with data
    html_content = _TEMPLATE.render(
        data=request.data.model_dump(),
        host=request.host,
        create_time_formatted=create_time_formatted
    )
    
    # Create CSS for page width
    page_css = CSS(string=f'@page {{ size: {request.width}px auto; margin: 0; }}')
    
    # Generate PDF using WeasyPrint
    html_doc = HTML(string=html_content, base_url=str(_TEMPLATE_PATH.parent))
    pdf_bytes = html_doc.write_pdf(stylesheets=[page_css])
    
    # Convert PDF to image
    # pdf2image returns a list of PIL Image objects
    images = convert_from_bytes(pdf_bytes, dpi=150)
    
    # Take the first page (should only be one page for our content)
    if images:
        img = images[0]
        
        # Convert to JPEG
        output_buffer = BytesIO()
        img.save(output_buffer, format='JPEG', quality=80)
        jpeg_bytes = output_buffer.getvalue()
        
        headers = {"complete": "true"}
        
        return Response(content=jpeg_bytes, media_type="image/jpeg", headers=headers)
    else:
        # Fallback: return empty response
        headers = {"complete": "false"}
        return Response(content=b"", media_type="image/jpeg", headers=headers)
