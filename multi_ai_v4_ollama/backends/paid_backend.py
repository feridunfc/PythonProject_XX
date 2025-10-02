# Placeholder for paid providers (OpenAI, etc.). Wire your API client here.
class PaidBackend:
    def __init__(self, role_to_model: dict, client):
        self.role_to_model = role_to_model
        self.client = client

    def generate(self, role: str, system: str, prompt: str) -> str:
        m = self.role_to_model[role]["model"]
        raise NotImplementedError("Implement your paid provider call here")
