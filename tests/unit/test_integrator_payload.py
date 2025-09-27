from pythonproject_xx.integrations.github_integrator import GitHubIntegrator, build_pr_body_from_report

def test_integrator_noop_when_no_token():
    integ = GitHubIntegrator(repo_full_name="owner/repo", token=None)
    body = build_pr_body_from_report("Daily Report", "# Run Report\n\nToplam kayıt: **0**")
    out = integ.create_pr(head="auto/123", title="Auto PR", body=body, base="main")
    assert out.get("skipped") is True
    assert "payload" in out