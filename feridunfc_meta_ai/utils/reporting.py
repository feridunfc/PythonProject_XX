# feridunfc_meta_ai/utils/reporting.py
from __future__ import annotations

import os
import csv
import base64
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Tuple

logger = logging.getLogger(__name__)


@dataclass
class _FlatTask:
    week: int
    task_id: str
    title: str
    agent_type: str
    status: str
    priority: int
    estimated_hours: float
    actual_hours: float
    dependencies: str
    created_at: str


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _flatten_tasks(sprint) -> List[_FlatTask]:
    rows: List[_FlatTask] = []
    for w in getattr(sprint, "weeks", []):
        week_no = getattr(w, "week_number", 0)
        for t in getattr(w, "tasks", []):
            rows.append(
                _FlatTask(
                    week=week_no,
                    task_id=getattr(t, "task_id", getattr(t, "id", "")),
                    title=getattr(t, "title", ""),
                    agent_type=getattr(t, "agent_type", ""),
                    status=getattr(t, "status", ""),
                    priority=getattr(t, "priority", 0),
                    estimated_hours=float(getattr(t, "estimated_hours", 0.0) or 0.0),
                    actual_hours=float(getattr(t, "actual_hours", 0.0) or 0.0),
                    dependencies=",".join(getattr(t, "dependencies", []) or []),
                    created_at=getattr(t, "created_at", ""),
                )
            )
    return rows


def _parse_dt(s: str) -> datetime:
    # ISO string (naive). Güvenli parse.
    try:
        return datetime.fromisoformat(s.split("Z")[0])
    except Exception:
        return datetime.utcnow()


def _write_placeholder_png(path: str) -> None:
    # 1x1 PNG (şeffaf) – bağımlılık gerekmeden geçerli bir dosya üretir
    b64 = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGMA"
        "AQAABQABDQottAAAAABJRU5ErkJggg=="
    )
    with open(path, "wb") as f:
        f.write(base64.b64decode(b64))


class ReportGenerator:
    def __init__(self, out_dir: str = "out") -> None:
        self.out_dir = out_dir
        _ensure_dir(self.out_dir)

    # ---- Excel/CSV ----
    def export_to_excel(self, sprint, filename: str = "sprint.xlsx") -> str:
        rows = _flatten_tasks(sprint)
        target = os.path.join(self.out_dir, filename)

        # Önce pandas+openpyxl deneyelim
        try:
            import pandas as pd  # type: ignore

            df = pd.DataFrame([r.__dict__ for r in rows])
            # openpyxl varsa xlsx yaz, yoksa csv fallback
            try:
                df.to_excel(target, index=False)  # requires openpyxl
                logger.info("Excel yazıldı: %s", target)
                return target
            except Exception as ex:
                logger.warning("Excel yazılamadı (%s). CSV'ye düşülüyor.", ex)
                csv_path = os.path.splitext(target)[0] + ".csv"
                df.to_csv(csv_path, index=False)
                return csv_path
        except Exception:
            # pandas yoksa stdlib csv
            csv_path = os.path.splitext(target)[0] + ".csv"
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=[
                        "week",
                        "task_id",
                        "title",
                        "agent_type",
                        "status",
                        "priority",
                        "estimated_hours",
                        "actual_hours",
                        "dependencies",
                        "created_at",
                    ],
                )
                writer.writeheader()
                for r in rows:
                    writer.writerow(r.__dict__)
            logger.info("Pandas yok: CSV yazıldı: %s", csv_path)
            return csv_path

    # ---- Gantt (PNG) ----
    # def generate_gantt_chart(self, sprint, filename: str = "gantt.png") -> str:
    #     path = os.path.join(self.out_dir, filename)
    #     tasks = _flatten_tasks(sprint)

    def generate_gantt_chart(self, sprint, filename: str = "gantt.png") -> str:
        path = os.path.join(self.out_dir, filename)
        tasks = _flatten_tasks(sprint)

        # GUI backend yerine 'Agg' ve düşük log seviyesi
        import matplotlib
        matplotlib.use("Agg")
        matplotlib.set_loglevel("WARNING")

        # try:
        #     import matplotlib.pyplot as plt
        #     import matplotlib.dates as mdates
        #

        # Basit bir çizelgeleme: sıralı diz, her task bir öncekinin sonuna başlar
        schedule: List[Tuple[str, datetime, datetime]] = []
        cursor = datetime.utcnow()
        for t in tasks:
            start = _parse_dt(t.created_at) if t.created_at else cursor
            # sıralı gitmek için en az cursor'dan başlat
            if start < cursor:
                start = cursor
            end = start + timedelta(hours=max(t.estimated_hours, 1e-6))
            schedule.append((f"[W{t.week}] {t.title}", start, end))
            cursor = end

        try:
            import matplotlib.pyplot as plt  # type: ignore
            import matplotlib.dates as mdates  # type: ignore

            fig = plt.figure(figsize=(8, 4))
            names = [n for (n, _, __) in schedule]
            starts = [mdates.date2num(s) for (_, s, __) in schedule]
            durations = [
                (e - s).total_seconds() / 3600.0 for (_, s, e) in schedule
            ]
            y = list(range(len(schedule)))

            plt.barh(y, durations, left=starts)
            plt.yticks(y, names)
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%m-%d %H:%M"))
            plt.gca().invert_yaxis()
            plt.tight_layout()
            fig.savefig(path, dpi=150)
            plt.close(fig)
            logger.info("Gantt PNG yazıldı: %s", path)
            return path
        except Exception as ex:
            logger.warning("matplotlib yok ya da hata oldu (%s). Placeholder PNG yazılıyor.", ex)
            _write_placeholder_png(path)
            return path

    # (Opsiyonel) JSON özet – istersen çağırırsın
    def export_summary_json(self, sprint, filename: str = "sprint.json") -> str:
        import json

        data = {
            "sprint_id": getattr(sprint, "id", getattr(sprint, "sprint_id", "")),
            "title": getattr(sprint, "title", getattr(sprint, "sprint_title", "")),
            "total_tasks": sprint.get_total_tasks(),
            "completed_tasks": sprint.get_completed_tasks(),
        }
        target = os.path.join(self.out_dir, filename)
        with open(target, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return target
