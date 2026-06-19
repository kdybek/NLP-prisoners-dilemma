"""
LLM Client for interacting with locally running models via Ollama
"""
import requests
import json
import logging
from typing import Optional, Dict, Any
from pydantic import BaseModel
import re

SEED = 0

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMResponse(BaseModel):
    action: str
    reason: str


class OllamaClient:
    def __init__(self, base_url: str, model: str):
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
        system_prompt: str,
        temperature: float = 0.7,
        top_p: float = 0.9,
        max_tokens: int = 50,
    ) -> str:
        global SEED

        try:
            payload = {
                "model": self.model,
                "system": system_prompt,
                "prompt": prompt,
                "stream": False,
                "think": False,
                "format": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["Cooperate", "Defect"]
                        }
                    },
                    "required": ["action"]
                },
                "options": {
                    "temperature": temperature,
                    "top_p": top_p,
                    "num_predict": max_tokens,
                    "seed": SEED,
                }
            }
            SEED += 1

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
            data = json.loads(response_text)

            action = data["action"]
            if action not in ["Cooperate", "Defect"]:
                raise ValueError(f"Invalid action: {action}")

            return LLMResponse(action=action, reason=data.get("reason", ""))

        except Exception as e:
            logger.error(f"Error parsing LLM response: {response_text}. Error: {e}")
            return None

    def get_decision(
        self,
        prompt: str,
        system_prompt: str,
        temperature: float,
    ) -> Optional[LLMResponse]:
        MAX_RETRIES = 3
        for attempt in range(MAX_RETRIES):
            logger.info(f"Requesting decision from {self.model}")

            response_text = self.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=50,
            )
            parsed = self.parse_llm_response(response_text)
            if parsed is not None:
                break

        if parsed is None:
            logger.error("Your model seems to be too stupid. Failed to get a valid response after multiple attempts.")
            raise Exception("Failed to get a valid response from the model after multiple attempts.")

        return parsed
