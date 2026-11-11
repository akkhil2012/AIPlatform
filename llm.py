"""OpenAI-compatible LLM adapter. Keys are never persisted."""
import json
import os
import urllib.request

class LLMError(RuntimeError):
    pass

def complete(messages, api_key=None, model=None, base_url=None, temperature=0.1):
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise LLMError("Configure OPENAI_API_KEY in the environment or enter an API key in the sidebar.")
    model = model or os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    endpoint = (base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")).rstrip("/") + "/chat/completions"
    if not endpoint.startswith("https://") and not endpoint.startswith("http://localhost:"):
        raise LLMError("Only HTTPS or localhost model endpoints are allowed.")
    payload = json.dumps({"model":model,"messages":messages,"temperature":temperature}).encode()
    request = urllib.request.Request(endpoint,data=payload,headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},method="POST")
    try:
        with urllib.request.urlopen(request,timeout=40) as response:
            result=json.load(response)
        return result["choices"][0]["message"]["content"]
    except Exception as exc:
        raise LLMError(f"Model request failed: {type(exc).__name__}: {str(exc)[:240]}") from exc

def ask(system, user, **kwargs):
    return complete([{"role":"system","content":system},{"role":"user","content":user}],**kwargs)

def parse_json(text):
    clean=text.strip()
    if clean.startswith("```"):
        clean=clean.split("\n",1)[1].rsplit("```",1)[0].strip()
        if clean.startswith("json"): clean=clean[4:].strip()
    return json.loads(clean)
