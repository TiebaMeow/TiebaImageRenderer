"""
HTML Kit-based renderer for converting HTML templates to images.

This module replaces the Playwright-based rendering with nonebot-plugin-htmlkit,
a lightweight HTML renderer based on litehtml.
"""

import asyncio
from pathlib import Path
from typing import Any, Optional
from pydantic import BaseModel
import jinja2

from .constants import DEFAULT_PAGE_WIDTH
from .config import config


class RenderParam(BaseModel):
    """Parameters for rendering HTML to image."""
    data: Any
    width: int | None = None
    timeout: int = 5000  # Kept for API compatibility, but not used with htmlkit
    host: str = f"http://{'localhost' if config.host == '0.0.0.0' else config.host}:{config.port}"


class HtmlKitRenderer:
    """
    Renderer class using nonebot-plugin-htmlkit.
    
    This replaces Playwright-based rendering with litehtml-based rendering,
    which is more lightweight and doesn't require a full browser.
    """
    
    def __init__(self):
        self._lock = asyncio.Lock()
        self._htmlkit_available = None
        self._html_to_pic = None
    
    async def _ensure_htmlkit(self):
        """Check if htmlkit is available and import it."""
        if self._htmlkit_available is None:
            async with self._lock:
                if self._htmlkit_available is None:
                    try:
                        # Import htmlkit dynamically
                        from nonebot_plugin_htmlkit import html_to_pic
                        self._html_to_pic = html_to_pic
                        self._htmlkit_available = True
                    except ImportError as e:
                        raise RuntimeError(
                            "nonebot-plugin-htmlkit is not installed. "
                            "Please install it following the instructions at: "
                            "https://github.com/nonebot/plugin-htmlkit#%E6%9E%84%E5%BB%BA%E8%AF%B4%E6%98%8E"
                        ) from e
    
    async def render(self, template_path: str | Path, params: RenderParam) -> tuple[bytes, bool]:
        """
        Render an HTML template to an image using htmlkit.
        
        Args:
            template_path: Path to the Jinja2 template file
            params: Rendering parameters including data and viewport width
            
        Returns:
            tuple: (image_bytes, is_complete) where is_complete is always True for htmlkit
        """
        await self._ensure_htmlkit()
        
        if not self._html_to_pic:
            raise RuntimeError("htmlkit not properly initialized")
        
        template_path = Path(template_path).absolute()
        
        # Prepare template data
        data = (
            params.data.model_dump()
            if isinstance(params.data, BaseModel)
            else params.data
        )
        if isinstance(data, dict):
            data["host"] = params.host
        
        # Load and render Jinja2 template
        template_dir = template_path.parent
        template_name = template_path.name
        
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dir),
            enable_async=True,
        )
        
        # Add custom filters
        def format_time(unix_timestamp):
            """Format Unix timestamp to readable date/time string."""
            from datetime import datetime
            dt = datetime.fromtimestamp(unix_timestamp)
            return f"{dt.month}月{dt.day}日 {dt.hour:02d}:{dt.minute:02d}"
        
        env.filters['format_time'] = format_time
        
        template = env.get_template(template_name)
        html_content = await template.render_async(**data if isinstance(data, dict) else {"data": data})
        
        # Render HTML to image using htmlkit
        width = params.width or DEFAULT_PAGE_WIDTH
        
        # Convert HTML to image
        screenshot = await self._html_to_pic(
            html=html_content,
            base_url=f"file://{template_path.parent.as_posix()}",
            max_width=float(width),
            dpi=96.0 * config.renderer_scale,
            image_format="jpeg",
            jpeg_quality=80,
            allow_refit=False,  # Keep fixed width like the original
        )
        
        # htmlkit rendering doesn't have a concept of "incomplete" rendering
        # so we always return True for compatibility
        return screenshot, True
    
    async def close(self):
        """
        Close the renderer.
        
        htmlkit doesn't need explicit cleanup like Playwright,
        but this method is kept for API compatibility.
        """
        async with self._lock:
            self._htmlkit_available = None
            self._html_to_pic = None


renderer = HtmlKitRenderer()
