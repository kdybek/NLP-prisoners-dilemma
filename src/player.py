"""
LLM Player for Prisoner's Dilemma
"""
import json
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
import random
from abc import ABC, abstractmethod
import src.globals as globals

logger = logging.getLogger(__name__)


class Player(ABC):
    def __init__(self, name: str):
        self.name = name
        self.decision_history: list = []

    @abstractmethod
    def _get_decision(
        self,
        game_state: Dict[str, Any]
    ) -> Dict[str, str]:
        """Return {'action': ..., 'reason': ...}"""
        pass

    def make_decision(
        self,
        game_state: Dict[str, Any]
    ) -> Dict[str, str]:
        decision = self._get_decision(game_state)

        self.decision_history.append({
            "round": game_state.get("round", 0),
            **decision
        })

        return decision

    def get_stats(self) -> Dict[str, Any]:
        cooperations = sum(
            1
            for d in self.decision_history
            if d["action"] == globals.COOP
        )

        defections = len(self.decision_history) - cooperations

        return {
            "name": self.name,
            "total_decisions": len(self.decision_history),
            "cooperations": cooperations,
            "defections": defections,
            "cooperation_rate": (
                cooperations / len(self.decision_history)
                if self.decision_history
                else 0
            ),
        }


class LLMPlayer(Player):

    def __init__(
        self,
        name: str,
        temperature: float,
        llm_client,
        prompts_dict: Dict[str, str]
    ):
        super().__init__(name)
        self.temperature = temperature
        self.llm_client = llm_client
        self.prompts = prompts_dict

    def build_prompts(self, game_state: Dict[str, Any]) -> str:
        base_prompt = self.prompts["game_prompt"]
        instruction_prompt = self.prompts["instruction_prompt"]
        persona_prompt = self.prompts["persona_prompt"]

        context = game_state["context"]

        system_prompt = f"{persona_prompt}\n{base_prompt}"
        prompt = f"{context}\n{instruction_prompt}"

        return system_prompt, prompt

    def _get_decision(
        self,
        game_state: Dict[str, Any]
    ) -> Dict[str, str]:
        system_prompt, prompt = self.build_prompts(game_state)

        response = self.llm_client.get_decision(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=self.temperature,
        )

        if response:
            return {
                "action": response.action,
                "reason": response.reason,
            }

        raise ValueError("LLM did not return a valid response")


class RandomPlayer(Player):

    def __init__(self, name, defection_probability: float = 0.5):
        super().__init__(name)
        self.defection_probability = defection_probability

    def _get_decision(
        self,
        game_state: Dict[str, Any]
    ) -> Dict[str, str]:

        action = (
            globals.DEFECT
            if random.random() < self.defection_probability
            else globals.COOP
        )

        return {
            "action": action,
            "reason": (
                "Random choice based on "
                "defection probability"
            ),
        }
