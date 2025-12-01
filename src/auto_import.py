import os
import importlib
from pathlib import Path

def auto_import_templates():
    """
    Automatically import all python files in src/template directory.
    """
    # Get the directory of the current file (src/)
    current_file = Path(__file__).resolve()
    src_dir = current_file.parent
    template_dir = src_dir / "template"

    if not template_dir.exists():
        return

    # Walk through the template directory
    for root, _, files in os.walk(template_dir):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                file_path = Path(root) / file
                
                # Calculate relative path from src directory
                try:
                    rel_path = file_path.relative_to(src_dir)
                except ValueError:
                    continue
                
                # Convert path to module notation
                # e.g. template/content/content_renderer.py -> template.content.content_renderer
                module_parts = rel_path.with_suffix("").parts
                module_name = ".".join(module_parts)
                
                # Construct the full module name including 'src' package
                # We try both with and without 'src.' prefix to be robust
                possible_names = [f"src.{module_name}", module_name]
                
                imported = False
                for name in possible_names:
                    try:
                        importlib.import_module(name)
                        print(f"[AutoImport] Successfully imported: {name}")
                        imported = True
                        break
                    except ImportError:
                        continue
                
                if not imported:
                    # Re-raise the last exception or print it for debugging
                    print(f"[AutoImport] Failed to import module for file: {rel_path}")
                    # Try to import again to capture the error
                    try:
                        importlib.import_module(possible_names[0])
                    except ImportError as e:
                        print(f"  Error details: {e}")

# Run the auto import when this module is imported
auto_import_templates()
