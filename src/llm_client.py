"""
LLM Client for interacting with locally running models via Ollama
"""
import requests
import json
import logging
from typing import Optional, Dict, Any
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMResponse(BaseModel):
    action: str
    reason: str


class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        self.base_url = base_url
        self.model = model
        self.api_generate_url = f"{base_url}/api/generate"
        self.check_connection()

    def _resolve_model_name(self, available_models: list[str]) -> bool:
        if self.model in available_models:
            return True

        latest_model = f"{self.model}:latest"
        if latest_model in available_models:
            logger.info(f"Using Ollama model tag: {latest_model}")
            self.model = latest_model
            return True

        return False

    def check_connection(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                available_models = [m['name']
                                    for m in response.json().get('models', [])]
                logger.info(f"Available models: {available_models}")
                if not self._resolve_model_name(available_models):
                    logger.warning(f"Model {self.model} not found. Available: {
                                   available_models}")
                    return False
                logger.info(f"Connected to Ollama with model: {self.model}")
                return True
            return False
        except requests.exceptions.ConnectionError:
            logger.error(f"Cannot connect to Ollama at {self.base_url}")
            logger.error("Make sure Ollama is running: ollama serve")
            return False

    def generate_response(
        self,
        prompt: str,
        temperature: float = 0.7,
        top_p: float = 0.9,
        max_tokens: int = 500,
    ) -> str:

        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "temperature": temperature,
                "top_p": top_p,
                "num_predict": max_tokens,
                "stream": False,
            }

            response = requests.post(self.api_generate_url, json=payload, timeout=60)

            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                logger.error(f"API Error: {response.status_code}")
                return ""

        except requests.exceptions.Timeout:
            logger.error("Request timeout - model taking too long to respond")
            return ""
        except requests.exceptions.ConnectionError:
            logger.error("Connection error - Ollama not responding")
            return ""
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return ""

    def parse_llm_response(self, response_text: str) -> Optional[LLMResponse]:
        try:
            # Try to find JSON in the response
            start_idx = response_text.find("{")
            end_idx = response_text.rfind("}") + 1

            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                parsed = json.loads(json_str)

                if "action" in parsed and "reason" in parsed:
                    return LLMResponse(
                        action=parsed["action"].strip(),
                        reason=parsed["reason"].strip()
                    )
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse JSON from response")

        return None

    def get_decision(
        self,
        full_prompt: str,
        persona: str = "baseline",
        temperature: float = 0.7,
    ) -> Optional[LLMResponse]:
        logger.info(f"Requesting decision from {self.model} with {persona} persona")

        response_text = self.generate_response(
            prompt=full_prompt,
            temperature=temperature,
            max_tokens=500
        )

        parsed = self.parse_llm_response(response_text)

        if not parsed:
            logger.error(f"Failed to parse response: {response_text}")
            return LLMResponse(action="Cooperate", reason="Unable to parse response")

        return parsed
