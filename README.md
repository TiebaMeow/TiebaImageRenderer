# TiebaImageRenderer

TiebaImageRenderer 是一个基于 **FastAPI**、**nonebot-plugin-htmlkit** 和 **Jinja2** 的高性能渲染服务，旨在将百度贴吧的内容（如帖子、评论等）动态渲染为图片。

## 🚀 功能特性

- **基于 Web 技术栈**: 使用 Jinja2 编写渲染模板，易于开发和维护样式。
- **高质量截图**: 利用 nonebot-plugin-htmlkit (基于 litehtml) 进行轻量级 HTML 渲染。
- **模块化设计**: 模板与业务逻辑分离，易于扩展新的渲染类型。
- **自动发现**: 自动加载 `src/template/` 下的渲染模块。

## 🛠️ 安装与使用

本项目使用 `uv` 进行依赖管理。

### 1. 环境准备

确保已安装 Python 3.12+ 和 `uv`。

```bash
# 安装项目依赖
uv sync

# 安装 nonebot-plugin-htmlkit (必须)
# 注意: htmlkit 需要从源码编译，请参考以下步骤：

# 1. 安装 xmake 构建工具
curl -fsSL https://xmake.io/shget.text | bash

# 2. 克隆 htmlkit 仓库并构建
git clone --recursive https://github.com/nonebot/plugin-htmlkit.git
cd plugin-htmlkit
uv sync --no-install-workspace
source .venv/bin/activate
xmake config -m releasedbg
xmake build
xmake install
uv sync --reinstall-package nonebot-plugin-htmlkit

# 3. 在主项目中安装构建好的 htmlkit
# 返回主项目目录并将 htmlkit 链接到项目环境
cd /path/to/TiebaImageRenderer
uv pip install /path/to/plugin-htmlkit
```

### 2. 启动服务

使用以下命令启动 API 服务：

```bash
uv run start.py
```

服务默认运行在 `http://localhost:39334`

## 🔌 API 调用示例

### 渲染帖子内容

将贴吧帖子内容渲染为图片。

- **接口地址**: `POST /renderer/content`
- **Content-Type**: `application/json`

#### 请求示例 (Python)

```python
import requests

url = "ttp://localhost:39334/renderer/content"

payload = {
    "data": {
        "title": "这是一个测试帖子标题",
        "text": "这里是帖子的正文内容，支持换行。\n测试测试。",
        "images": [h
            "图片哈希1" 
        ],
        "user": {
            "username": "贴吧用户",
            "portrait": "tb.1.xxx.xxx",
            "level": 12
        },
        "create_time": 1701388800,
        "prefix": "前缀信息(可选)",
        "suffix": "后缀信息(可选)"
    },
    "width": 400  # 图片宽度
}

response = requests.post(url, json=payload)

if response.status_code == 200:
    with open("result.jpg", "wb") as f:
        f.write(response.content)
    print("渲染成功，已保存为 result.jpg")
else:
    print(f"渲染失败: {response.text}")
```

#### 请求参数说明

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| `data` | Object | 渲染所需的数据对象 |
| `data.title` | String | 帖子标题 |
| `data.text` | String | 帖子正文 |
| `data.images` | List[String] | 图片 URL 列表 |
| `data.user` | Object | 用户信息 |
| `data.create_time` | Integer | 发帖时间戳 |
| `width` | Integer | (可选) 渲染视口的宽度，默认 400 |

## 📂 项目结构

```text
TiebaImageRenderer/
├── src/
│   ├── api/            # FastAPI 核心服务
│   ├── template/       # 渲染模板目录
│   │   └── content/    # 示例：内容渲染模块
│   │       ├── content_renderer.py     # 路由与数据模型
│   │       └── template_htmlkit.html   # Jinja2 渲染模板
│   ├── renderer_htmlkit.py  # htmlkit 渲染引擎封装
│   └── ...
├── config.toml         # 配置文件
└── start.py            # 启动脚本
```

## 📝 开发新模板

1. 在 `src/template/` 下创建一个新目录（例如 `my_feature`）。
2. 创建 `template.html`，使用 Jinja2 模板语法编写界面，可以使用模板变量如 `{{ variable }}`。
3. 创建 `my_feature_renderer.py`，定义 Pydantic 模型并注册 FastAPI 路由。
4. 在渲染器中调用 `renderer.render(template_path, request)` 来渲染模板。
5. 重启服务，新路由将被自动加载。
