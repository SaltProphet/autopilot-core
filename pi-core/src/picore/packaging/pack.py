"""
Assemble bundle folder, write bundle_manifest.json, produce ZIP-ready output.
"""
import json
import shutil
from pathlib import Path
from ..models.core import BundleManifest

class Packager:
    @staticmethod
    def assemble_bundle(bundle_dir: Path, manifest: BundleManifest):
        bundle_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = bundle_dir / "bundle_manifest.json"
        tmp_path = manifest_path.with_suffix(".tmp")
        with tmp_path.open("w", encoding="utf-8") as f:
            f.write(manifest.json(indent=2, sort_keys=True, ensure_ascii=False))
        tmp_path.replace(manifest_path)

    @staticmethod
    def zip_bundle(bundle_dir: Path, zip_path: Path):
        shutil.make_archive(str(zip_path.with_suffix("")), 'zip', root_dir=bundle_dir)
