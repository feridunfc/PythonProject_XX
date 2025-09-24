
from typing import List
import pandas as pd
import matplotlib.pyplot as plt

class ReportGenerator:
    def generate_gantt_chart(self, sprint, save_path: str | None = None):
        fig, ax = plt.subplots(figsize=(10, 6))
        tasks = []
        for wk in sprint.weeks:
            for t in wk.tasks:
                tasks.append((t.title, wk.number, wk.start_date, wk.end_date, t.estimated_hours))
        ylabels = [t[0] for t in tasks]
        widths = [t[4] for t in tasks]
        lefts = [t[1] for t in tasks]
        ax.barh(ylabels, widths, left=lefts)
        ax.set_xlabel("Saat (genişlik)")
        ax.set_ylabel("Görev")
        ax.set_title(f"Gantt – {sprint.title}")
        ax.invert_yaxis()
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=180, bbox_inches="tight")
        return fig

    def export_to_excel(self, sprint, filename: str):
        rows = []
        for wk in sprint.weeks:
            for t in wk.tasks:
                rows.append({
                    "Week": wk.number,
                    "Week Start": wk.start_date,
                    "Week End": wk.end_date,
                    "Task": t.title,
                    "Agent": t.agent_type,
                    "Status": t.status,
                    "Estimated Hours": t.estimated_hours,
                    "Actual Hours": t.actual_hours,
                })
        df = pd.DataFrame(rows)
        with pd.ExcelWriter(filename) as writer:
            df.to_excel(writer, sheet_name='Task Summary', index=False)
            pivot = df.pivot_table(index='Week', values='Estimated Hours', aggfunc='sum').reset_index()
            pivot.to_excel(writer, sheet_name='Weekly Hours', index=False)
        return filename
