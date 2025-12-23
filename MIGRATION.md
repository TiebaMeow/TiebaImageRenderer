# htmlkit Migration Guide

本文档说明从 Playwright 渲染器迁移到 nonebot-plugin-htmlkit 的详细信息。

## 概述

本项目已从基于 Playwright 的浏览器渲染迁移到基于 litehtml 的轻量级 HTML 渲染器 (nonebot-plugin-htmlkit)。

### 主要变化

| 方面 | 之前 (Playwright) | 现在 (htmlkit) |
|------|------------------|----------------|
| 渲染引擎 | Chromium 浏览器 | litehtml (C++ 库) |
| 模板语言 | Vue.js | Jinja2 |
| 依赖大小 | ~200MB | ~10MB |
| 渲染速度 | 较慢 (启动浏览器) | 快速 (原生渲染) |
| CSS 支持 | 完整支持 | 基础 CSS 支持 |
| JavaScript | 完整支持 | 不支持 |

## 安装 htmlkit

htmlkit 需要从源码编译，因为它包含 C++ 组件。

### 系统要求

- Python 3.10+
- Git
- C++ 编译器 (gcc/clang)
- CMake
- xmake 构建工具

### 详细安装步骤

```bash
# 1. 安装 xmake (构建工具)
# 推荐方法: 下载并审查脚本
wget https://xmake.io/shget.text -O xmake-install.sh
less xmake-install.sh  # 审查脚本内容
bash xmake-install.sh
source ~/.xmake/profile  # 或重启终端

# 备选方法: 使用包管理器
# Ubuntu/Debian: sudo add-apt-repository ppa:xmake-io/xmake && sudo apt install xmake
# macOS: brew install xmake
# 其他系统: https://xmake.io/#/guide/installation

# 2. 克隆 htmlkit 仓库
git clone --recursive https://github.com/nonebot/plugin-htmlkit.git
cd plugin-htmlkit

# 3. 创建虚拟环境并安装依赖
uv sync --no-install-workspace
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 4. 配置 xmake 项目
xmake config -m releasedbg

# 5. 构建 (第一次可能需要 10-30 分钟)
xmake build

# 6. 安装到虚拟环境
xmake install
uv sync --reinstall-package nonebot-plugin-htmlkit

# 7. 返回主项目并安装
cd /path/to/TiebaImageRenderer
uv pip install /path/to/plugin-htmlkit
```

### 验证安装

```python
python -c "from nonebot_plugin_htmlkit import html_to_pic; print('htmlkit installed successfully!')"
```

## API 兼容性

### 保持不变的部分

- HTTP API 端点: `POST /renderer/content` 保持不变
- 请求格式: `ContentRenderRequest` 模型保持不变
- 响应格式: 返回 JPEG 图片，headers 包含 `complete` 字段

### 内部变化

```python
# 之前
from src.renderer import renderer, RenderParam

# 现在
from src.renderer_htmlkit import renderer, RenderParam
```

## 模板迁移指南

### Vue.js → Jinja2 转换

**之前 (Vue.js)**:
```html
<div id="app">
  <h1>{{ data.title }}</h1>
  <p>{{ data.text }}</p>
</div>

<script>
const { createApp, reactive } = Vue;
createApp({
  setup() {
    const data = reactive({ title: '', text: '' });
    window.init = (injectedData) => {
      Object.assign(data, injectedData);
      // Signal completion
      const div = document.createElement('div');
      div.id = 'render-complete';
      document.body.appendChild(div);
    };
    return { data };
  }
}).mount('#app');
</script>
```

**现在 (Jinja2)**:
```html
<div>
  <h1>{{ title }}</h1>
  <p>{{ text }}</p>
</div>
```

### 关键区别

1. **数据注入方式**
   - 之前: JavaScript `window.init(data)` 动态注入
   - 现在: Jinja2 服务器端渲染时注入

2. **完成信号**
   - 之前: 需要在模板中添加 `#render-complete` 元素
   - 现在: 不需要，htmlkit 自动处理

3. **循环和条件**
   ```html
   <!-- Vue.js -->
   <div v-if="data.images">
     <img v-for="img in data.images" :src="img">
   </div>
   
   <!-- Jinja2 -->
   {% if images %}
   <div>
     {% for img in images %}
     <img src="{{ img }}">
     {% endfor %}
   </div>
   {% endif %}
   ```

4. **自定义过滤器**
   ```python
   # 在 renderer_htmlkit.py 中注册
   env.filters['format_time'] = format_time
   ```
   
   ```html
   <!-- 在模板中使用 -->
   {{ create_time | format_time }}
   ```

## 功能对比

### 支持的功能

✅ 基础 HTML 结构  
✅ CSS 样式 (box model, flexbox, 基础定位)  
✅ 图片加载 (本地文件、HTTP、data URI)  
✅ 自定义字体  
✅ Jinja2 模板引擎  
✅ 自适应宽度  

### 不支持的功能

❌ JavaScript 执行  
❌ 复杂 CSS (animations, transforms, grid)  
❌ 视频/音频  
❌ Canvas/SVG (部分支持)  
❌ Web fonts (@font-face 有限支持)  

## 性能对比

基于相同内容的渲染测试:

| 指标 | Playwright | htmlkit |
|------|-----------|---------|
| 首次渲染 | ~2-3秒 | ~100-200ms |
| 内存占用 | ~300MB | ~50MB |
| 并发能力 | 受浏览器限制 | 更高 |

## 故障排除

### htmlkit 安装失败

```bash
# 确保安装了所有依赖
sudo apt-get install build-essential cmake git

# 清理并重新构建
cd plugin-htmlkit
xmake clean --all
xmake build
```

### 模板渲染不正确

1. 检查 Jinja2 语法是否正确
2. 验证传递的数据结构
3. 使用 `verify_migration.py` 测试模板

### 图片加载失败

htmlkit 支持多种图片加载方式:
- 本地文件: `file:///path/to/image.png`
- HTTP: `http://example.com/image.png`
- Data URI: `data:image/png;base64,...`

确保 `base_url` 设置正确，用于解析相对路径。

### CSS 样式不生效

htmlkit 基于 litehtml，CSS 支持有限:
- 使用简单的布局 (flexbox > grid)
- 避免使用 CSS 变量
- 测试兼容性: https://github.com/litehtml/litehtml/wiki/Supported-CSS-features

## 回退到 Playwright

如果遇到问题需要临时回退:

```python
# 在 content_renderer.py 中
from src.renderer_playwright_deprecated import renderer, RenderParam

# 使用旧模板
screenshot, is_complete = await renderer.render(
    Path(__file__).parent / "template_vue_deprecated.html", request
)
```

⚠️ 注意: 旧的 Playwright 代码标记为已弃用，不建议长期使用。

## 额外资源

- [htmlkit 官方文档](https://github.com/nonebot/plugin-htmlkit)
- [litehtml CSS 支持](https://github.com/litehtml/litehtml/wiki)
- [Jinja2 模板文档](https://jinja.palletsprojects.com/)

## 贡献

如果发现问题或有改进建议，请提交 Issue 或 Pull Request。
