"""Build a local review ZIP from an explicit set of project assets."""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "ecommerce-delivery-customer-satisfaction"


def main():
    paths = [ROOT / p for p in ("README.md", "requirements.txt", ".gitignore")]
    for folder, patterns in (("scripts", ("*.py",)), ("docs", ("*.md",)),
                              ("reports", ("*.md", "*.json")),
                              ("reports/figures", ("*.png", "*.svg"))):
        for pattern in patterns:
            paths.extend(sorted((ROOT / folder).glob(pattern)))
    paths = sorted(set(paths))
    if not all(p.is_file() for p in paths):
        raise ValueError("Required package assets missing.")
    report = json.loads((ROOT / "reports/workbook_inventory.json").read_text())
    source = ROOT / report["source"]
    if source.exists() and hashlib.sha256(source.read_bytes()).hexdigest() != report["sha256"]:
        raise ValueError("Source changed; rebuild and review reports before packaging.")
    manifest = {"package": PREFIX, "source_file_omitted": report["source"],
                "expected_source_sha256": report["sha256"],
                "files": {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}
    destination = ROOT / "dist"
    destination.mkdir(exist_ok=True)
    target = destination / f"{PREFIX}.zip"
    with ZipFile(target, "w", ZIP_DEFLATED) as archive:
        for path in paths:
            archive.write(path, f"{PREFIX}/{path.relative_to(ROOT).as_posix()}")
        archive.writestr(f"{PREFIX}/manifest.json", json.dumps(manifest, indent=2) + "\n")
    with ZipFile(target) as archive:
        if archive.testzip() is not None:
            raise ValueError("ZIP integrity check failed.")
        for name, digest in manifest["files"].items():
            if hashlib.sha256(archive.read(f"{PREFIX}/{name}")).hexdigest() != digest:
                raise ValueError(f"Archive hash mismatch: {name}")
    print(f"Created {target.relative_to(ROOT)} ({len(paths)} project files plus manifest)")


if __name__ == "__main__":
    main()
