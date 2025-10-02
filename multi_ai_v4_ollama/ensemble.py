def run_ensemble(backends, role, system_prompt, prompt_variants, eval_fn, top_k=1):
    candidates = []
    for b in backends:
        for v in prompt_variants:
            content = b.generate(role, system_prompt, v["prompt"])
            candidates.append(content)
    scored = [eval_fn(c) for c in candidates]
    paired = list(zip(candidates, scored))
    paired.sort(key=lambda t: t[1].get("final_score", 0), reverse=True)
    best = paired[0] if paired else ("", {"final_score": -1})
    return {"best": {"content": best[0], "score": best[1]}, "all": paired[:max(3, top_k)]}
