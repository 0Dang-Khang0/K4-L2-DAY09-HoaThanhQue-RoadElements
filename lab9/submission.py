"""Kiểm tra submission đủ file và đúng cấu trúc tối thiểu."""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

from .common import load_lab, lock_values, sha256_file
from .team import load_team, mode_line


def _check_tasks(base: Path, config: Dict[str, object]) -> Tuple[List[str], bool]:
    lines: List[str] = []
    gaps = False
    for task in config["task_order"]:
        directory = base / "submission" / task
        xml_path, lock_path = directory / "annotations.xml", directory / "lock.txt"
        required = (xml_path, lock_path, directory / "reference.txt", directory / "compare.md")
        missing = [path.name for path in required if not path.is_file()]
        if missing:
            lines.append(f"✗ {task}: thiếu " + ", ".join(missing))
            gaps = True
            continue
        values = lock_values(lock_path)
        if values.get("sha256") != sha256_file(xml_path):
            lines.append(f"✗ {task}: annotations.xml không khớp SHA-256 trong lock.txt")
            gaps = True
        else:
            lines.append(f"✓ {task}: annotations.xml, lock.txt, reference.txt, compare.md đầy đủ và hash khớp")
    return lines, gaps


def _nonempty_rows(path: Path) -> Tuple[List[str], List[Dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        header = reader.fieldnames or []
        rows = []
        for row in reader:
            normalized = {
                str(key): (";".join(value) if isinstance(value, list) else (value or "")).strip()
                for key, value in row.items()
                if key is not None
            }
            if any(normalized.values()):
                rows.append(normalized)
        return header, rows


def _check_log(base: Path, name: str, config: Dict[str, object]) -> Tuple[List[str], bool, List[Dict[str, str]]]:
    path = base / "submission" / name
    spec = config["logs"][name]
    if not path.is_file():
        return [f"✗ {name}: thiếu file"], True, []
    try:
        header, rows = _nonempty_rows(path)
    except (OSError, csv.Error, UnicodeError) as error:
        return [f"✗ {name}: không đọc được CSV ({error})"], True, []
    lines: List[str] = []
    gaps = False
    if header != spec["columns"]:
        lines.append(f"✗ {name}: header phải đúng thứ tự trong lab.json")
        gaps = True
    tasks = list(config["task_order"])
    counts = {task: 0 for task in tasks}
    for number, row in enumerate(rows, 2):
        errors = []
        for field in spec.get("required", []):
            if not row.get(field, ""):
                errors.append(f"thiếu {field}")
        for field, allowed in spec.get("enums", {}).items():
            value = row.get(field, "")
            if value and value not in allowed:
                errors.append(f"{field}={value} không hợp lệ")
        task = row.get("task", "")
        if task not in tasks:
            errors.append(f"task={task or '(trống)'} không hợp lệ")
        else:
            counts[task] += 1
        if errors:
            lines.append(f"✗ {name} dòng {number}: " + "; ".join(errors))
            gaps = True
    minimum = int(spec.get("min_rows_per_task", 0))
    for task, count in counts.items():
        prefix = "✓" if count >= minimum else "✗"
        lines.append(f"{prefix} {name} {task}: {count} dòng (cần ít nhất {minimum})")
        if count < minimum:
            gaps = True
    total_minimum = int(spec.get("min_rows_total", 0))
    if total_minimum:
        prefix = "✓" if len(rows) >= total_minimum else "✗"
        lines.append(f"{prefix} {name}: {len(rows)} dòng tổng (cần ít nhất {total_minimum})")
        if len(rows) < total_minimum:
            gaps = True
    return lines, gaps, rows


def _check_documents(base: Path, config: Dict[str, object]) -> Tuple[List[str], bool]:
    lines: List[str] = []
    gaps = False
    marker = str(config.get("todo_marker", "TODO"))
    for name in config.get("documents", []):
        path = base / "submission" / str(name)
        if not path.is_file() or not path.read_text(encoding="utf-8").strip():
            lines.append(f"✗ {name}: thiếu hoặc rỗng")
            gaps = True
            continue
        count = path.read_text(encoding="utf-8").count(marker)
        if count:
            lines.append(f"✗ {name}: còn {count} marker {marker}")
            gaps = True
        else:
            lines.append(f"✓ {name}: đã điền và không còn marker {marker}")
    return lines, gaps


def check_submission(base: Path) -> Tuple[List[str], bool]:
    """Trả từng dòng kiểm tra và cờ có thiếu/sai."""
    config = load_lab(base)
    members = load_team(base)
    task_lines, gaps = _check_tasks(base, config)
    lines = [mode_line(base), *task_lines]
    for task in config["task_order"]:
        reference_path = base / "submission" / task / "reference.txt"
        if not reference_path.is_file():
            continue
        reference = lock_values(reference_path)
        lock_path = base / "submission" / task / "lock.txt"
        lock = lock_values(lock_path) if lock_path.is_file() else {}
        try:
            opened_at = datetime.fromisoformat(reference.get("opened_at", ""))
            locked_at = datetime.fromisoformat(lock.get("locked_at", ""))
            relocked_after_open = locked_at > opened_at
        except (TypeError, ValueError):
            continue
        if relocked_after_open:
            lines.append(f"! {task}: khoá lại sau khi mở reference — ghi lý do trong decision log")
    if members and not any((base / "submission").glob("*/peer-*.txt")):
        lines.append("✗ Chế độ nhóm: chưa có submission/*/peer-*.txt")
        gaps = True
    comparison_lines, comparison_gaps, _ = _check_log(base, "comparison_log.csv", config)
    decision_lines, decision_gaps, decision_rows = _check_log(base, "decision_log.csv", config)
    document_lines, document_gaps = _check_documents(base, config)
    lines.extend(comparison_lines)
    lines.extend(decision_lines)
    lines.extend(document_lines)
    gaps = gaps or comparison_gaps or decision_gaps or document_gaps
    ratified = sum(row.get("status") == "ratified" for row in decision_rows)
    if ratified:
        lines.append(f"✓ decision_log.csv: {ratified} dòng đã ratify")
    else:
        lines.append("! decision_log.csv: chưa có dòng nào ratified — ratify ở bước cuối (phút 225–235)")
    lines.append("Đây là kiểm tra đủ file, không phải điểm.")
    return lines, gaps
