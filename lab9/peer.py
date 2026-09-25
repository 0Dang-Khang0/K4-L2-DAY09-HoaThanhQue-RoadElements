"""So bài đã khoá với file của một bạn cùng nhóm."""

from __future__ import annotations

from pathlib import Path
import re
from typing import List
import unicodedata

from . import LabError
from .common import load_lab, require_intact_lock, require_task, sha256_file
from .compare import Comparison, compare_locked_with, write_html_comparison
from .locking import lock_code


def _slug(name: str) -> str:
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]+", "-", ascii_name).strip("-") or "ban-cung-nhom"


def _normalized_code(code: str) -> str:
    return "".join(character for character in code.upper() if not character.isspace() and character != "-")


def _text_report(report: Comparison, task: str, name: str) -> str:
    lines = [
        f"So sánh peer {task} với {name} (bạn cùng nhóm)",
        f"Khớp: {report.matched}",
        f"Chỉ bài mình: {report.only_learner}",
        f"Chỉ bài {name}: {report.only_other}",
        f"Khác attribute: {report.attribute_disagreements}",
        "Khác biệt:",
    ]
    if report.differences:
        lines.extend(
            f"- {difference.sample} · {difference.text} [{difference.error_type}]"
            for difference in report.differences
        )
    else:
        lines.append("- Không có khác biệt.")
    return "\n".join(lines) + "\n"


def run_peer(base: Path, task: str, source: Path, code: str, name: str) -> List[str]:
    """Xác minh mã khoá rồi tạo report peer riêng biệt."""
    teammate = name.strip()
    if not teammate:
        raise LabError("NAME không được để trống.")
    config = load_lab(base)
    require_task(task, config)
    locked_xml, _, own_lock = require_intact_lock(
        base,
        task,
        f"Chưa khoá {task} — chạy make lock TASK={task} FILE=… trước khi so peer.",
        f"submission/{task}/annotations.xml đã đổi sau khi khoá — chạy lại make lock với đúng file "
        "export đã khoá để khôi phục (sửa tay XML không được tính).",
    )
    if not source.is_file():
        raise LabError(f"Không thấy file {source}.")
    digest = sha256_file(source)
    if _normalized_code(code) != _normalized_code(lock_code(digest)):
        raise LabError(f"Mã khoá không khớp file của {teammate} — xin lại đúng file đã khoá.")
    if digest == own_lock.get("sha256") or source.read_bytes() == locked_xml.read_bytes():
        raise LabError("File peer giống hệt bài đã khoá của bạn — chọn file của bạn cùng nhóm.")
    label = f"bài của {teammate}"
    report, _, manifest_task, other, learner = compare_locked_with(base, task, source, label)
    output = base / "submission" / task
    output.mkdir(parents=True, exist_ok=True)
    stem = f"peer-{_slug(teammate)}"
    text_path = output / f"{stem}.txt"
    html_path = output / f"{stem}.html"
    text_path.write_text(_text_report(report, task, teammate), encoding="utf-8")
    write_html_comparison(html_path, report, manifest_task, other, learner, label)
    return [
        f"✓ Peer {task} với {teammate}: {report.matched} khớp; {report.only_learner} chỉ bài mình; "
        f"{report.only_other} chỉ bài {teammate}; {report.attribute_disagreements} khác attribute.",
        f"✓ Report: {html_path.relative_to(base)} và {text_path.relative_to(base)}",
    ]
