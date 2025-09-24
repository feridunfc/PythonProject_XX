# feridunfc_meta_ai/config/agent_config.py
AGENT_MODEL_MAP = {
    "architect": [
        ("openai",  "gpt-4o-mini"),
        ("gemini",  "gemini-1.5-flash"),   # ek
        ("deepseek","deepseek-chat"),
    ],
    "codegen": [
        ("openai",  "gpt-4o-mini"),
        ("gemini",  "gemini-1.5-flash"),   # ek
        ("deepseek","deepseek-chat"),
    ],
    "tester": [
        ("openai",  "gpt-4o-mini"),
        ("gemini",  "gemini-1.5-flash"),   # ek
        ("deepseek","deepseek-chat"),
    ],
    "critic": [
        ("openai",  "gpt-4o-mini"),
        ("gemini",  "gemini-1.5-flash"),   # ek
        ("deepseek","deepseek-chat"),
    ],
    "debugger": [
        ("openai",  "gpt-4o-mini"),
        ("gemini",  "gemini-1.5-flash"),
    ],
    "integrator": [
        ("openai",  "gpt-4o-mini"),
        ("gemini",  "gemini-1.5-flash"),
    ],
}
