# TiebaImageRenderer Copilot Instructions

This project is a specialized service for rendering Tieba (Chinese forum) content into images using **FastAPI**, **Playwright**, and **Vue.js**.

## 🏗 Architecture Overview

- **Core Service (`src/api/`)**: A FastAPI application that serves as the entry point.
- **Rendering Engine (`src/renderer.py`)**: A singleton `Renderer` class wrapping Playwright. It loads HTML templates, injects data, and captures screenshots.
- **Templates (`src/template/`)**: Modular rendering components. Each subdirectory typically contains:
  - A Python file defining the data model and registering the API route.
  - An HTML file (often using Vue.js) for the visual layout.
- **Auto-Discovery**: `src/auto_import.py` automatically imports modules in `src/template/` on startup, registering their routes.

## 🚀 Developer Workflow

- **Run Server**: `uv run start.py`
- **Configuration**: Managed via `config.toml`. Defaults are defined in `src/config.py`.
- **Dependencies**: Managed with `uv` in `pyproject.toml`.

## 🧩 Creating a New Renderer

To add a new image generation feature (e.g., for a new type of post):

1.  **Create Directory**: `src/template/<feature_name>/`
2.  **Create Template (`template.html`)**:
    - Use Vue.js (global build) for reactivity.
    - **Contract**:
        - Implement `window.init(data)` to receive JSON data from the Python backend.
        - Append an element with `id="render-complete"` to the DOM when rendering is finished (e.g., in Vue's `mounted` or `updated` hook).
3.  **Create Handler (`<feature_name>_renderer.py`)**:
    - Define a Pydantic model for the input data.
    - Register a POST route using `@app.post`.
    - Call `renderer.render(template_path, request_data)`.

### Example Handler Pattern

```python
from pathlib import Path
from fastapi import Response
from pydantic import BaseModel
from src.renderer import renderer, RenderParam
from src.api.server import app

class MyData(BaseModel):
    title: str
    content: str

class MyRequest(RenderParam):
    data: MyData

@app.post("/renderer/my-feature")
async def render_my_feature(request: MyRequest):
    # Template path must be absolute or resolved relative to __file__
    template_path = Path(__file__).parent / "template.html"
    
    screenshot, is_complete = await renderer.render(template_path, request)
    
    return Response(content=screenshot, media_type="image/jpeg")
```

## 🎨 Frontend (Vue) Contract

```html
<script>
  const { createApp, ref } = Vue;
  
  createApp({
    setup() {
      const data = ref({});
      
      // 1. Receive data from Playwright
      window.init = (injectedData) => {
        data.value = injectedData;
        
        // 2. Signal completion (use nextTick if needed)
        setTimeout(() => {
            const div = document.createElement('div');
            div.id = 'render-complete';
            document.body.appendChild(div);
        }, 100); 
      };
      
      return { data };
    }
  }).mount('#app');
</script>
```

## 🛠 Common Patterns

- **Path Handling**: Always use `pathlib.Path` for file system operations.
- **Resource Proxy**: Use `src/api/routes/resource.py` endpoints (`/resources/image/...`) to fetch images from Tieba to avoid CORS/Referer issues in the renderer.
- **Host Injection**: The renderer automatically injects `host` into the data object, allowing templates to reference local API resources dynamically.
