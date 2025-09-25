import pandas as pd
import matplotlib.pyplot as plt

class ReportGenerator:
    def export_to_excel(self, sprint, filename: str):
        rows = []
        for w in sprint.weeks:
            for t in w.tasks:
                rows.append({
                    "Week": w.number, "Task": t.title, "Agent": t.agent_type,
                    "Status": t.status, "Estimated": t.estimated_hours, "Actual": t.actual_hours
                })
        df = pd.DataFrame(rows); df.to_excel(filename, index=False); return filename

    def generate_gantt_chart(self, sprint, filename: str):
        fig, ax = plt.subplots(figsize=(10, max(3, len([t for w in sprint.weeks for t in w.tasks])*0.4)))
        y=0
        for w in sprint.weeks:
            for t in w.tasks:
                ax.barh(y, max(1, t.estimated_hours/2), left=w.number, align="center")
                ax.text(w.number+0.1, y, t.title, va="center")
                y += 1
        ax.set_xlabel("Week #"); ax.set_ylabel("Tasks"); ax.set_title(f"Gantt – {sprint.title}")
        ax.invert_yaxis(); fig.tight_layout(); fig.savefig(filename); plt.close(fig); return filename
