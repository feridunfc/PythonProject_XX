from tenacity import retry, stop_after_attempt, wait_exponential
import ollama

class OllamaBackend:
    def __init__(self, role_to_model: dict):
        self.role_to_model = role_to_model

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate(self, role: str, system: str, prompt: str) -> str:
        m = self.role_to_model[role]["model"]
        messages = [{"role": "system", "content": system},
                    {"role": "user", "content": prompt}]
        resp = ollama.chat(model=m, messages=messages, options={"temperature": 0.3, "num_predict": 2048})
        return resp["message"]["content"]
