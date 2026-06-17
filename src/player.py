"""
LLM Player for Prisoner's Dilemma
"""
import json
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PlayerConfig:
    name: str
    model: str
    company: str
    persona: str = "baseline"
    temperature: float = 0.7


class LLMPlayer:
    
    def __init__(self, config: PlayerConfig, llm_client, prompts_dict: Dict[str, str]):
        self.config = config
        self.llm_client = llm_client
        self.prompts = prompts_dict
        self.decision_history: list = []
    
    def build_prompt(self, game_state: Dict[str, Any]) -> str:
        base_prompt = self.prompts.get("Contana_game_prompt", "")
        instruction_prompt = self.prompts.get("instruction_prompts", "")
        
        persona_prompts = self.prompts.get("persona_prompt", {})
        persona_template = persona_prompts.get(
            self.config.persona,
            persona_prompts.get("baseline", "")
        )
        
        persona = persona_template.format(
            model=self.config.model,
            company=self.config.company
        )
        
        context = game_state.get("context", "")
        
        full_prompt = f"""{persona}{base_prompt}{context}{instruction_prompt}"""
        
        return full_prompt
    
    def make_decision(self, game_state: Dict[str, Any]) -> Optional[Dict[str, str]]:
        prompt = self.build_prompt(game_state)
        
        response = self.llm_client.get_decision(
            full_prompt=prompt,
            persona=self.config.persona,
            temperature=self.config.temperature
        )
        
        if response:
            decision = {
                "action": response.action,
                "reason": response.reason
            }
            self.decision_history.append({
                "round": game_state.get("round", 0),
                **decision
            })
            return decision
        
        logger.warning(f"Failed to get decision from {self.config.name}")
        return {"action": "Cooperate", "reason": "Default action due to error"}
    
    def get_stats(self) -> Dict[str, Any]:
        cooperations = sum(
            1 for d in self.decision_history
            if d["action"] == "Cooperate"
        )
        defections = len(self.decision_history) - cooperations
        
        return {
            "name": self.config.name,
            "model": self.config.model,
            "persona": self.config.persona,
            "total_decisions": len(self.decision_history),
            "cooperations": cooperations,
            "defections": defections,
            "cooperation_rate": cooperations / len(self.decision_history) if self.decision_history else 0,
        }
