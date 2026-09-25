"""Khoá export CVAT bằng SHA-256 trước khi mở reference."""

from __future__ import annotations

from collections import Counter
from datetime import datetime
import hashlib
from pathlib import Path
from typing import Dict, List

from . import LabError
from .common import load_lab, load_manifest, lock_values, read_json, require_task
from .cvat_xml import parse_bytes, xml_bytes


def lock_code(digest: str) -> str:
    """Đổi SHA-256 thành mã ngắn dùng để xác nhận file."""
    short = digest[:8].upper()
    return short[:4] + "-" + short[4:]


def _allowed_labels(base: Path, task: str) -> set:
    schema_path = base / "data" / task / "schema.json"
    if not schema_path.is_file():
        raise LabError(f"Thiếu data/{task}/schema.json — khôi phục bằng git checkout -- data/{task}/schema.json.")
    schema = read_json(schema_path)
    return {str(item.get("name", "")) for item in schema}


def _current_lock_text(task: str, digest: str, code: str, counts: Dict[str, int], relock_count: int) -> str:
    shapes = ", ".join(f"{name}={count}" for name, count in sorted(counts.items())) or "không có"
    return "\n".join(
        [
            f"task: {task}",
            f"sha256: {digest}",
            f"code: {code}",
            f"locked_at: {datetime.now().astimezone().isoformat(timespec='seconds')}",
            f"shapes: {shapes}",
            f"relock_count: {relock_count}",
        ]
    ) + "\n"


def lock_export(base: Path, task: str, source: Path, relock: bool = False) -> List[str]:
    """Kiểm tra export, copy XML và ghi lock.txt."""
    config = load_lab(base)
    require_task(task, config)
    manifest = load_manifest(base)
    manifest_task = manifest.get("tasks", {}).get(task)
    if not isinstance(manifest_task, dict):
        raise LabError(f"data/manifest.json thiếu task {task}.")
    data = xml_bytes(source)
    document = parse_bytes(data, manifest_task.get("core", []))
    if task == "traffic_light" and document.sizes:
        # CVAT for images bỏ track id; chỉ CVAT for video giữ được track và outside.
        raise LabError("traffic_light phải export bằng CVAT for video 1.1 (file này là CVAT for images). Export lại rồi khoá.")
    labels = {item.label for item in document.objects}
    unknown = sorted(labels - _allowed_labels(base, task))
    if unknown:
        raise LabError("Export dùng label ngoài schema: " + ", ".join(unknown) + ". Sửa label trong CVAT rồi export lại.")
    core = set(manifest_task.get("core", []))
    if not any(item.sample in core and item.kind != "tag" for item in document.objects):
        raise LabError("Không có shape nào trên mẫu core — kiểm tra đúng task rồi export lại.")
    missing = [sample for sample in manifest_task.get("core", []) if document.sizes and sample not in document.sizes]
    warnings = []
    if missing:
        shown = ", ".join(missing[:3]) + (f" và {len(missing) - 3} ảnh khác" if len(missing) > 3 else "")
        warnings.append(f"! Core {shown} không có trong export — kiểm tra đã upload đủ ảnh của task.")
    if task == "traffic_light":
        # CVAT for video ghi mỗi Shape thành track chỉ có 1 frame hiện, rồi outside ở frame sau.
        visible_frames = Counter(item.track_id for item in document.objects if item.kind != "tag")
        single = sum(1 for count in visible_frames.values() if count == 1)
        if single:
            warnings.append(
                f"! {single} track đèn chỉ có 1 frame — thường là vẽ bằng Shape. Vẽ lại bằng Track (GUIDE mục 3.3)."
            )
    digest = hashlib.sha256(data).hexdigest()
    code = lock_code(digest)
    directory = base / "submission" / task
    destination = directory / "annotations.xml"
    lock_path = directory / "lock.txt"
    old_text = lock_path.read_text(encoding="utf-8") if lock_path.is_file() else ""
    old_values = lock_values(lock_path) if old_text else {}
    if old_values.get("sha256") == digest:
        if not destination.is_file() or hashlib.sha256(destination.read_bytes()).hexdigest() != digest:
            destination.write_bytes(data)
        return warnings + [
            f"✓ Mã khoá {task}: {old_values.get('code', code)} — ghi mã này vào bài; làm nhóm thì gửi mã + file "
            f"submission/{task}/annotations.xml cho bạn cùng nhóm."
        ]
    if old_text and not relock:
        raise LabError(
            f"{task} đã khoá với file khác. Chạy lại với RELOCK=1 "
            "(hoặc thêm --relock nếu dùng python lab9.py)."
        )
    directory.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    counts = Counter(item.label for item in document.objects)
    relock_count = int(old_values.get("relock_count", "0")) + (1 if old_text else 0)
    new_text = _current_lock_text(task, digest, code, counts, relock_count)
    if old_text:
        new_text += "history:\n  --- previous lock ---\n" + "".join("  " + line + "\n" for line in old_text.splitlines())
    lock_path.write_text(new_text, encoding="utf-8")
    return warnings + [
        f"✓ Mã khoá {task}: {code} — ghi mã này vào bài; làm nhóm thì gửi mã + file "
        f"submission/{task}/annotations.xml cho bạn cùng nhóm."
    ]
