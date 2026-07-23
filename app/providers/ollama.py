"""Ollama LLM provider — connects to a local Ollama instance."""

from __future__ import annotations

import json
import urllib.request
import urllib.error
from typing import Any

from app.providers.base import Provider


class OllamaProvider(Provider):
    """Provider that calls a local Ollama instance for text generation."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama3.2",
        temperature: float = 0.7,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.temperature = temperature

    def capabilities(self) -> list[str]:
        return ["text", "chat"]

    def invoke(self, capability: str, payload: dict[str, Any]) -> dict[str, Any]:
        prompt = payload.get("prompt", "")
        system = payload.get("system", "")

        if capability == "chat":
            return self._chat(system=system, user=prompt)
        return self._generate(prompt=prompt, system=system)

    def _generate(self, prompt: str, system: str = "") -> dict[str, Any]:
        """Call Ollama /api/generate endpoint."""
        body = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": self.temperature},
        }
        if system:
            body["system"] = system

        response = self._post("/api/generate", body)
        return {
            "output": response.get("response", ""),
            "model": response.get("model", self.model),
            "done": response.get("done", False),
        }

    def _chat(self, system: str = "", user: str = "") -> dict[str, Any]:
        """Call Ollama /api/chat endpoint."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": user})

        body = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": self.temperature},
        }

        response = self._post("/api/chat", body)
        message = response.get("message", {})
        return {
            "output": message.get("content", ""),
            "model": response.get("model", self.model),
            "done": response.get("done", False),
        }

    def _post(self, endpoint: str, body: dict) -> dict:
        """Make a POST request to the Ollama API."""
        url = f"{self.base_url}{endpoint}"
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise ConnectionError(
                f"Cannot connect to Ollama at {self.base_url}. "
                f"Make sure 'ollama serve' is running. Error: {exc}"
            ) from exc
        except Exception as exc:
            raise RuntimeError(f"Ollama request failed: {exc}") from exc
