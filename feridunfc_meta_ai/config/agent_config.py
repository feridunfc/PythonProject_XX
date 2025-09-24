
# feridunfc_meta_ai/config/agent_config.py
# Sağlayıcı sırası: gemini -> openai -> deepseek; agent'a göre model tercihleri
AGENT_MODEL_MAP = {
    "architect": [("gemini", "gemini-1.5-flash"), ("openai", "gpt-4o-mini"), ("deepseek", "deepseek-chat")],
    "codegen":   [("gemini", "gemini-1.5-flash"), ("openai", "gpt-4o-mini"), ("deepseek", "deepseek-coder")],
    "critic":    [("gemini", "gemini-1.5-flash"), ("openai", "gpt-4o-mini")],
    "tester":    [("gemini", "gemini-1.5-flash"), ("openai", "gpt-4o-mini")],
    "debugger":  [("gemini", "gemini-1.5-flash"), ("openai", "gpt-4o-mini")],
    "integrator":[("gemini", "gemini-1.5-flash"), ("openai", "gpt-4o-mini")],
}
