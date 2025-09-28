from typing import Dict, Any, List

class LinterTool:
    """Minimal stub: verilen kod üzerinde basit kontroller döner.
    Gerçek entegrasyon ileride ruff/flake8 çağrısına çevrilebilir.
    """
    def run(self, code: str, config_path: str | None = None) -> Dict[str, Any]:
        issues: List[Dict[str, Any]] = []
        # Çok basit bir uyarı örneği: tab karakteri var mı?
        if "\t" in code:
            issues.append({"rule": "no-tabs", "message": "Tab character found"})
        return {"ok": True, "issues": issues}