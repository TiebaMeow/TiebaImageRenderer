"""
Verification script for the htmlkit migration.

This script tests that:
1. Jinja2 templates render correctly with sample data
2. The template structure is valid
3. Custom filters work as expected

Note: This does NOT test actual image generation, which requires
nonebot-plugin-htmlkit to be installed and compiled.

Some imports are done inside functions to gracefully handle missing
optional dependencies (like FastAPI) without failing the entire script.
"""

import asyncio
import tempfile
from pathlib import Path
from datetime import datetime
import jinja2


async def test_template_rendering():
    """Test that the Jinja2 template renders correctly."""
    
    print("Testing Jinja2 template rendering...")
    
    # Sample data matching ContentData model
    sample_data = {
        "host": "http://localhost:39334",
        "title": "测试帖子标题",
        "text": "这是测试内容\n支持多行文本",
        "images": ["test_hash_1", "test_hash_2"],
        "user": {
            "username": "测试用户",
            "portrait": "tb.1.test.portrait",
            "level": 12
        },
        "create_time": int(datetime.now().timestamp()),
        "prefix": "<div>前缀内容</div>",
        "suffix": "<div>后缀内容</div>"
    }
    
    # Load template
    template_path = Path(__file__).parent / "src" / "template" / "content" / "template_htmlkit.html"
    
    if not template_path.exists():
        print(f"❌ Template not found at: {template_path}")
        return False
    
    print(f"✓ Template found at: {template_path}")
    
    # Setup Jinja2 environment
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_path.parent),
        enable_async=True,
    )
    
    # Add format_time filter
    def format_time(unix_timestamp):
        """Format Unix timestamp to readable date/time string."""
        dt = datetime.fromtimestamp(unix_timestamp)
        return f"{dt.month}月{dt.day}日 {dt.hour:02d}:{dt.minute:02d}"
    
    env.filters['format_time'] = format_time
    
    # Render template
    try:
        template = env.get_template("template_htmlkit.html")
        html_content = await template.render_async(**sample_data)
        
        print(f"✓ Template rendered successfully ({len(html_content)} bytes)")
        
        # Basic validation
        checks = [
            ("title" in html_content, "Title present"),
            ("测试帖子标题" in html_content, "Title content present"),
            ("测试用户" in html_content, "Username present"),
            ("Lv.12" in html_content, "User level present"),
            ("/resources/portrait/" in html_content, "Portrait URL present"),
            ("/resources/image/" in html_content, "Image URL present"),
        ]
        
        all_passed = True
        for check, description in checks:
            if check:
                print(f"✓ {description}")
            else:
                print(f"❌ {description}")
                all_passed = False
        
        # Save rendered HTML for inspection
        output_path = Path(tempfile.gettempdir()) / "rendered_template.html"
        output_path.write_text(html_content)
        print(f"✓ Rendered HTML saved to: {output_path}")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Template rendering failed: {e}")
        # Import traceback only when needed for error reporting
        import traceback
        traceback.print_exc()
        return False


async def test_api_compatibility():
    """
    Test that the API models are compatible.
    
    Note: Imports are done inside this function to handle cases where
    FastAPI and other web dependencies may not be installed (e.g., in
    lightweight testing environments).
    """
    
    print("\nTesting API compatibility...")
    
    try:
        # Delayed imports to handle optional dependencies gracefully
        from src.template.content.content_renderer import (
            ContentData,
            ContentRenderRequest,
            User
        )
        from src.renderer_htmlkit import RenderParam
        
        print("✓ All imports successful")
        
        # Test model instantiation
        user = User(username="test", portrait="test.portrait", level=5)
        content_data = ContentData(
            title="Test",
            text="Test content",
            images=[],
            user=user,
            create_time=12345678,
        )
        request = ContentRenderRequest(data=content_data, width=550)
        
        print("✓ Models instantiate correctly")
        print(f"✓ Request host default: {request.host}")
        print(f"✓ Request width: {request.width}")
        
        return True
        
    except Exception as e:
        print(f"❌ API compatibility test failed: {e}")
        # Import traceback only when needed for error reporting
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all verification tests."""
    
    print("=" * 60)
    print("htmlkit Migration Verification")
    print("=" * 60)
    print()
    
    results = []
    
    # Test template rendering
    results.append(("Template Rendering", await test_template_rendering()))
    
    # Test API compatibility
    results.append(("API Compatibility", await test_api_compatibility()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)
    
    for name, passed in results:
        status = "✓ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {name}")
    
    all_passed = all(r[1] for r in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All verifications passed!")
        print("\nNext steps:")
        print("1. Install nonebot-plugin-htmlkit following README instructions")
        print("2. Start the server: python start.py")
        print("3. Test the /renderer/content endpoint with a POST request")
    else:
        print("❌ Some verifications failed. Please check the errors above.")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
