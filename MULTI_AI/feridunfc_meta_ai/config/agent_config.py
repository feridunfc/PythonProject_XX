# feridunfc_meta_ai/config/agent_config.py
AGENT_MODEL_MAP = {
    # Sağlayıcı sırası: gemini -> openai -> deepseek
    "architect":  [("gemini", "gemini-1.5-flash"), ("openai","gpt-4o-mini"), ("deepseek","deepseek-chat")],
    "codegen":    [("gemini", "gemini-1.5-flash"), ("openai","gpt-4o-mini"), ("deepseek","deepseek-coder")],
    "critic":     [("gemini", "gemini-1.5-flash"), ("openai","gpt-4o-mini")],
    "tester":     [("gemini", "gemini-1.5-flash"), ("openai","gpt-4o-mini")],

    # Eksik olanlar:
    "integrator": [("gemini", "gemini-1.5-flash"), ("openai","gpt-4o-mini"), ("mock","mock")],
    "debugger":   [("gemini", "gemini-1.5-flash"), ("openai","gpt-4o-mini"), ("mock","mock")],

    # İleride başka roller kullanılıyorsa buraya ekleyin:
    # "knowledge":  [("gemini","gemini-1.5-flash"), ("openai","gpt-4o-mini"), ("mock","mock")],
    # "planner":    [("gemini","gemini-1.5-flash"), ("openai","gpt-4o-mini"), ("mock","mock")],
}
