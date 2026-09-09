"""
Self Skill Engine for ConsciousCore V1.
Manages discovery, registration, lifecycle states, dependencies, and execution of self-skills.
"""

from typing import Dict, Any, List, Optional
import time

class Skill:
    def __init__(
        self,
        skill_id: str,
        name: str,
        category: str = "learned",
        procedure: str = "",
        permissions: Optional[List[str]] = None,
        state: str = "LOADED",
        confidence: float = 0.9,
        success_rate: float = 1.0
    ):
        self.skill_id = skill_id
        self.name = name
        self.category = category
        self.procedure = procedure
        self.permissions = permissions or ["READ"]
        self.state = state
        self.confidence = confidence
        self.success_rate = success_rate
        self.execution_count = 0
        self.last_used = None

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        self.execution_count += 1
        self.last_used = time.time()
        return {
            "skill_id": self.skill_id,
            "status": "SUCCESS",
            "result": f"Executed procedure '{self.procedure}' with params {params}",
            "execution_count": self.execution_count
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "name": self.name,
            "category": self.category,
            "procedure": self.procedure,
            "permissions": self.permissions,
            "state": self.state,
            "confidence": self.confidence,
            "success_rate": self.success_rate,
            "execution_count": self.execution_count,
            "last_used": self.last_used
        }

class SkillsEngine:
    def __init__(self):
        self.skills: Dict[str, Skill] = {}
        # Seed built-in native skills
        self.register_skill(Skill("skill_001", "System Diagnostic Check", "system", "run_system_diagnostics", state="ACTIVE"))
        self.register_skill(Skill("skill_002", "FTS Memory Search", "knowledge", "execute_fts_retrieval", state="ACTIVE"))

    def register_skill(self, skill: Skill) -> Skill:
        self.skills[skill.skill_id] = skill
        return skill

    def discover_skill(self, name: str, category: str, procedure: str) -> Skill:
        skill_id = f"skill_{len(self.skills) + 1:03d}"
        skill = Skill(skill_id, name, category, procedure, state="DISCOVERED")
        return self.register_skill(skill)

    def list_skills(self) -> List[Dict[str, Any]]:
        return [s.to_dict() for s in self.skills.values()]

    def get_skill(self, skill_id: str) -> Optional[Skill]:
        return self.skills.get(skill_id)
