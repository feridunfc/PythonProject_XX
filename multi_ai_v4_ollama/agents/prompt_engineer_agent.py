from pydantic import BaseModel
import json

class PromptPack(BaseModel):
    role: str
    system_prompt: str
    variants: list[dict]  # [{name, prompt}]
    policies: list[str] = []

PE_SYSTEM = "Senior prompt engineer. Output ONLY valid JSON."

PE_TEMPLATE = '''Role: {role}
Brief JSON: {brief}
Policies: ["no-external-network","return-only-code","respect-schema"]
Return JSON: {{
  "role": "{role}",
  "system_prompt": "short role & strict rules",
  "variants": [
    {{"name": "v1-structured", "prompt": "ROLE={role}; Follow schema; Output only code/JSON as required."}},
    {{"name": "v2-terse", "prompt": "ROLE={role}; Minimal verbose; Deterministic; Output only the artifact."}}
  ],
  "policies": ["no-external-network","return-only-code","respect-schema"]
}}'''

def build_prompts(backend, role: str, brief_json: str) -> PromptPack:
    out = backend.generate("architect", PE_SYSTEM, PE_TEMPLATE.format(role=role, brief=brief_json))
    return PromptPack(**json.loads(out))
