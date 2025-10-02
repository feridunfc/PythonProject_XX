import json, random

def judge_plans(plan_json_list: list[str]) -> dict:
    # Simple placeholder: valid JSON gains base score; randomly add a small jitter
    scored = []
    for pj in plan_json_list:
        try:
            json.loads(pj); base = 2.0
        except Exception:
            base = 0.0
        score = base + random.uniform(0, 3)
        scored.append({"plan": pj, "score": score})
    best = max(scored, key=lambda x: x["score"]) if scored else {"plan": "", "score": -1}
    return {"candidates": scored, "winner": best}
