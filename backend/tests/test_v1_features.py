from app.core.skills_engine import SkillsEngine
from app.core.learning_engine import LearningEngine
from app.core.ai_network import AINetworkBus
from app.core.code_lab import CodeLab
from app.core.diagnostics import DiagnosticsEngine

def test_skills_engine():
    engine = SkillsEngine()
    skills = engine.list_skills()
    assert len(skills) >= 2
    sk = engine.discover_skill("Test Skill", "learned", "run_test")
    assert sk.skill_id.startswith("skill_")
    res = sk.execute({"param": 1})
    assert res["status"] == "SUCCESS"

def test_learning_engine():
    engine = LearningEngine()
    lessons = engine.get_lessons()
    assert len(lessons) >= 1
    new_les = engine.record_experience("run_task", "completed", True)
    assert new_les["id"].startswith("les_")

def test_ai_network_bus():
    bus = AINetworkBus()
    agents = bus.list_agents()
    assert len(agents) >= 5
    sess = bus.start_session("Test Debate", ["Researcher", "Critic"])
    assert sess["session_id"].startswith("session_")

def test_code_lab():
    lab = CodeLab()
    prop = lab.submit_proposal("Fix Bug", "Developer", "main.py", "diff...")
    assert prop.proposal_id.startswith("proposal_")
    approved = lab.approve_proposal(prop.proposal_id)
    assert approved.status == "APPROVED"

def test_diagnostics():
    res = DiagnosticsEngine.check_myself()
    assert res["status"] == "HEALTHY"
    assert res["components"]["identity"]["ok"] is True
