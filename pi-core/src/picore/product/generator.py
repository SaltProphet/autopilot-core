"""
Implements template_pack generation ONLY. Generates real files, hashes, atomic writes.
Fails for unsupported ProductType.
"""
import os
import hashlib
from pathlib import Path
from typing import List, Dict
from ..models.core import ProductSpec, Artifact, ProductType

class TemplatePackGenerator:
    @staticmethod
    def generate(spec: ProductSpec, out_dir: Path) -> List[Artifact]:
        if spec.product_type != ProductType.template_pack:
            raise RuntimeError("Only template_pack generation is supported.")
        files = {
            "README.md": f"# {spec.value_prop}\n\nSee templates/ for usage.",
            "LICENSE.txt": TemplatePackGenerator.mit_license(),
            "templates/base_template.md": "# Base Template\n\nInstructions...",
            "templates/advanced_template.md": "# Advanced Template\n\nAdvanced usage...",
            "examples/filled_example.md": "# Example\n\nFilled out example.",
            "docs/usage.md": "# Usage\n\nHow to use the template pack.",
            "docs/customization.md": "# Customization\n\nHow to customize.",
            "listing.md": f"# Listing\n\n{spec.value_prop}"
        }
        artifacts = []
        for rel_path, content in files.items():
            file_path = out_dir / rel_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            tmp_path = file_path.with_suffix(file_path.suffix + ".tmp")
            with tmp_path.open("w", encoding="utf-8") as f:
                f.write(content)
            tmp_path.replace(file_path)
            sha = TemplatePackGenerator.sha256_of_file(file_path)
            artifacts.append(Artifact(
                path=str(rel_path),
                kind="markdown" if rel_path.endswith(".md") else "text",
                sha256=sha,
                bytes=os.path.getsize(file_path)
            ))
        return artifacts

    @staticmethod
    def sha256_of_file(path: Path) -> str:
        h = hashlib.sha256()
        with path.open("rb") as f:
            while True:
                chunk = f.read(8192)
                if not chunk:
                    break
                h.update(chunk)
        return h.hexdigest()

    @staticmethod
    def mit_license() -> str:
        return (
            "MIT License\n\n"
            "Copyright (c) 2026 pi-core\n\n"
            "Permission is hereby granted, free of charge, to any person obtaining a copy "
            "of this software and associated documentation files (the \"Software\"), to deal "
            "in the Software without restriction, including without limitation the rights "
            "to use, copy, modify, merge, publish, distribute, sublicense, and/or sell "
            "copies of the Software, and to permit persons to whom the Software is "
            "furnished to do so, subject to the following conditions:\n\n"
            "THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR "
            "IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, "
            "FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE "
            "AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER "
            "LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, "
            "OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE "
            "SOFTWARE."
        )
