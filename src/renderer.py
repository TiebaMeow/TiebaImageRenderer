import json
import asyncio
from pathlib import Path
from typing import Any, Optional
from pydantic import BaseModel

from playwright.async_api import async_playwright, Browser, Playwright

from .constants import DEFAULT_PAGE_WIDTH
from .config import config


class RenderParam(BaseModel):
    data: Any
    width: int | None = None
    timeout: int = 5000
    host: str = f"http://{'localhost' if config.host == '0.0.0.0' else config.host}:{config.port}"


class Renderer:
    def __init__(self):
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self._lock = asyncio.Lock()

    async def _ensure_browser(self):
        if self.browser is None:
            async with self._lock:
                if self.playwright is None:
                    self.playwright = await async_playwright().start()
                if self.browser is None:
                    self.browser = await self.playwright.chromium.launch(
                        args=["--no-sandbox", "--disable-setuid-sandbox"]
                    )

    async def render(self, path: str | Path, params: RenderParam) -> tuple[bytes, bool]:
        await self._ensure_browser()
        if not self.browser:
            raise RuntimeError("Browser failed to start")

        page = await self.browser.new_page()
        try:
            url = Path(path).absolute().as_uri()
            width = params.width or DEFAULT_PAGE_WIDTH
            await page.set_viewport_size({"width": width, "height": 100})
            await page.goto(url)

            # Inject data
            data = (
                params.data.model_dump()
                if isinstance(params.data, BaseModel)
                else params.data
            )
            data["host"] = params.host
            await page.evaluate("(data) => window.init(data)", data)

            # Wait for render completion signal
            is_complete = True
            try:
                await page.wait_for_selector(
                    "#render-complete", state="attached", timeout=params.timeout
                )
            except Exception:
                is_complete = False

            screenshot = await page.screenshot(full_page=True, type="jpeg", quality=80)
            return screenshot, is_complete
        finally:
            await page.close()

    async def close(self):
        async with self._lock:
            if self.browser:
                await self.browser.close()
                self.browser = None
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None


renderer = Renderer()
