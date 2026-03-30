"""
Unified LLM client.

Provides a single interface for sending prompts to any supported LLM
provider. Modules use this instead of crafting raw HTTP requests.
"""

from __future__ import annotations

import httpx
import structlog
from typing import Any, Dict, List, Optional

from metallm.base.target import LLMTarget, GenericHTTPTarget, Target

logger = structlog.get_logger()


class LLMClient:
    """
    Send prompts to LLM APIs and return response text.

    Supports OpenAI, Anthropic, Ollama, and generic HTTP endpoints.
    Designed for security testing — intentionally does NOT retry on
    failure so modules can observe raw error behavior.
    """

    def __init__(self, target: Target, timeout: float = 30.0):
        self.target = target
        self.timeout = timeout

    def send(
        self,
        prompt: str,
        system_prompt: str = "",
        messages: Optional[List[Dict[str, str]]] = None,
        **kwargs: Any,
    ) -> Optional[str]:
        """
        Send a prompt and return the response text.

        Args:
            prompt: User message to send.
            system_prompt: Optional system prompt override.
            messages: Optional full message history (overrides prompt).
            **kwargs: Provider-specific options (temperature, max_tokens, etc.)

        Returns:
            Response text or None on failure.
        """
        if isinstance(self.target, LLMTarget):
            provider = (self.target.provider or "").lower()
            dispatch = {
                "openai": self._send_openai,
                "anthropic": self._send_anthropic,
                "ollama": self._send_ollama,
                "google": self._send_google,
            }
            handler = dispatch.get(provider, self._send_openai_compat)
            return handler(prompt, system_prompt, messages, **kwargs)

        # Fallback: generic HTTP POST
        return self._send_generic(prompt, **kwargs)

    # ------------------------------------------------------------------
    # Provider implementations
    # ------------------------------------------------------------------

    def _send_openai(
        self, prompt: str, system_prompt: str,
        messages: Optional[List[Dict]], **kw: Any,
    ) -> Optional[str]:
        target: LLMTarget = self.target  # type: ignore
        headers = {
            "Authorization": f"Bearer {target.api_key}",
            "Content-Type": "application/json",
        }

        msgs = messages or []
        if not msgs:
            sys = system_prompt or target.system_prompt
            if sys:
                msgs.append({"role": "system", "content": sys})
            msgs.append({"role": "user", "content": prompt})

        payload: Dict[str, Any] = {
            "model": target.model_name or "gpt-4o",
            "messages": msgs,
            "max_tokens": kw.get("max_tokens", target.max_tokens),
            "temperature": kw.get("temperature", target.temperature),
        }

        url = target.url or "https://api.openai.com/v1/chat/completions"
        return self._post_json(url, headers, payload, ["choices", 0, "message", "content"])

    def _send_openai_compat(
        self, prompt: str, system_prompt: str,
        messages: Optional[List[Dict]], **kw: Any,
    ) -> Optional[str]:
        """OpenAI-compatible API (vLLM, LiteLLM, LocalAI, etc.)."""
        return self._send_openai(prompt, system_prompt, messages, **kw)

    def _send_anthropic(
        self, prompt: str, system_prompt: str,
        messages: Optional[List[Dict]], **kw: Any,
    ) -> Optional[str]:
        target: LLMTarget = self.target  # type: ignore
        headers = {
            "x-api-key": target.api_key,
            "Content-Type": "application/json",
            "anthropic-version": target.api_version or "2023-06-01",
        }

        msgs = messages or [{"role": "user", "content": prompt}]

        payload: Dict[str, Any] = {
            "model": target.model_name or "claude-sonnet-4-20250514",
            "max_tokens": kw.get("max_tokens", target.max_tokens),
            "messages": msgs,
        }
        sys = system_prompt or target.system_prompt
        if sys:
            payload["system"] = sys

        url = target.url or "https://api.anthropic.com/v1/messages"
        return self._post_json(url, headers, payload, ["content", 0, "text"])

    def _send_ollama(
        self, prompt: str, system_prompt: str,
        messages: Optional[List[Dict]], **kw: Any,
    ) -> Optional[str]:
        target: LLMTarget = self.target  # type: ignore

        payload: Dict[str, Any] = {
            "model": target.model_name or "llama3.2",
            "prompt": prompt,
            "stream": False,
        }
        sys = system_prompt or target.system_prompt
        if sys:
            payload["system"] = sys

        url = target.url or "http://localhost:11434/api/generate"
        return self._post_json(url, {}, payload, ["response"])

    def _send_google(
        self, prompt: str, system_prompt: str,
        messages: Optional[List[Dict]], **kw: Any,
    ) -> Optional[str]:
        target: LLMTarget = self.target  # type: ignore
        model = target.model_name or "gemini-2.0-flash"

        url = (
            target.url
            or f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        )

        if "?" not in url:
            url += f"?key={target.api_key}"

        payload: Dict[str, Any] = {
            "contents": [{"parts": [{"text": prompt}]}],
        }

        return self._post_json(url, {}, payload, ["candidates", 0, "content", "parts", 0, "text"])

    def _send_generic(self, prompt: str, **kw: Any) -> Optional[str]:
        """Send to an arbitrary HTTP endpoint."""
        target = self.target
        headers = dict(target.headers) if target.headers else {}
        if target.api_key:
            headers.setdefault("Authorization", f"Bearer {target.api_key}")

        payload = {"prompt": prompt, **kw}

        data = self._post_json_raw(target.url, headers, payload)
        if data is None:
            return None

        # Try common response shapes
        for key in ("response", "text", "content", "output", "result", "message"):
            if key in data:
                val = data[key]
                if isinstance(val, str):
                    return val
                if isinstance(val, list) and val:
                    return str(val[0])
                return str(val)

        return str(data)

    # ------------------------------------------------------------------
    # HTTP helpers
    # ------------------------------------------------------------------

    def _post_json(
        self,
        url: str,
        headers: Dict[str, str],
        payload: Dict[str, Any],
        response_path: list,
    ) -> Optional[str]:
        """POST JSON and extract a nested value from the response."""
        data = self._post_json_raw(url, headers, payload)
        if data is None:
            return None

        # Walk the response path
        obj: Any = data
        for key in response_path:
            if isinstance(obj, dict):
                obj = obj.get(key)
            elif isinstance(obj, list) and isinstance(key, int):
                obj = obj[key] if key < len(obj) else None
            else:
                return None
            if obj is None:
                return None

        return str(obj)

    def _post_json_raw(
        self,
        url: str,
        headers: Dict[str, str],
        payload: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """POST JSON and return the parsed response dict."""
        try:
            with httpx.Client(verify=self.target.verify_ssl) as client:
                resp = client.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout,
                )
                resp.raise_for_status()
                return resp.json()
        except httpx.HTTPStatusError as e:
            logger.warning(
                "llm_client.http_error",
                url=url,
                status=e.response.status_code,
                body=e.response.text[:500],
            )
            return None
        except Exception as e:
            logger.warning("llm_client.error", url=url, error=str(e))
            return None
