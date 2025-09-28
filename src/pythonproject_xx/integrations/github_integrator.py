from __future__ import annotations
import os
from typing import Optional, Dict, Any

def _pygithub_available() -> bool:
    try:
        import github  # type: ignore
        return True
    except Exception:
        return False

class GitHubIntegrator:
    """
    Basit PR açma iskeleti.
    - Token veya PyGithub yoksa NO-OP döner (CI güvenli).
    """
    def __init__(self, repo_full_name: Optional[str] = None, token: Optional[str] = None) -> None:
        self.repo_full_name = repo_full_name or os.getenv("GITHUB_REPOSITORY")
        self.token = token or os.getenv("GITHUB_TOKEN")

    def create_pr(self, head: str, title: str, body: str, base: str = "main") -> Dict[str, Any]:
        if not self.token or not self.repo_full_name or not _pygithub_available():
            return {"skipped": True, "reason": "no token/repo or PyGithub missing", "payload": {"head": head, "base": base, "title": title, "body": body}}

        from github import Github  # type: ignore
        gh = Github(self.token)
        repo = gh.get_repo(self.repo_full_name)
        pr = repo.create_pull(title=title, body=body, head=head, base=base)
        return {"skipped": False, "url": pr.html_url, "number": pr.number}

def build_pr_body_from_report(title: str, report_md: str) -> str:
    return f"## {title}\n\n{report_md}\n"