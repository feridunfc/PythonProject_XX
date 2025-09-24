from feridunfc_meta_ai.config.agent_config import AGENT_MODEL_MAP

def choose_model(agent_role: str, prefer_costly=False, skip_provider: str | None = None, force_provider: str | None = None):
    pairs = AGENT_MODEL_MAP.get(agent_role, [])
    if force_provider:
        for prov, mdl in pairs:
            if prov == force_provider:
                return prov, mdl
    for prov, mdl in pairs:
        if prov != skip_provider:
            return prov, mdl
    # fallback: ilkini dön
    return pairs[0] if pairs else ("deepseek", "deepseek-chat")
