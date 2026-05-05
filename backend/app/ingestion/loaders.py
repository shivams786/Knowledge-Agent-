import json
from pathlib import Path
from typing import BinaryIO


TEXT_EXTENSIONS = {
    ".md",
    ".txt",
    ".py",
    ".java",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".json",
    ".yaml",
    ".yml",
    ".go",
    ".rs",
    ".sql",
    ".html",
    ".css",
}
CODE_EXTENSIONS = {".py", ".java", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".sql", ".html", ".css"}


def detect_file_type(filename: str) -> str:
    suffix = Path(filename).suffix.lower().lstrip(".") or "txt"
    return suffix


def is_code_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in CODE_EXTENSIONS


def extract_text(path: Path) -> str:
    """Extract text from supported enterprise document/code formats."""

    suffix = path.suffix.lower()
    if suffix == ".pdf":
        try:
            from pypdf import PdfReader

            reader = PdfReader(str(path))
            return "\n".join(page.extract_text() or "" for page in reader.pages).strip()
        except Exception as exc:  # pragma: no cover - depends on optional PDF internals
            raise ValueError(f"Unable to extract PDF text: {exc}") from exc
    if suffix in TEXT_EXTENSIONS or not suffix:
        return path.read_text(encoding="utf-8", errors="ignore")
    return path.read_text(encoding="utf-8", errors="ignore")


def pretty_json_if_needed(filename: str, text: str) -> str:
    if Path(filename).suffix.lower() == ".json":
        try:
            return json.dumps(json.loads(text), indent=2, sort_keys=True)
        except json.JSONDecodeError:
            return text
    return text


def save_upload(file_obj: BinaryIO, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(file_obj.read())
