from native.rules.rule_engine import NativeRuleEngine
from native.intent.intent_engine import NativeIntentEngine
from app.core.contradiction_engine import ContradictionEngine

def test_native_rule_engine():
    engine = NativeRuleEngine()
    actions = engine.evaluate({"ram_usage": 95})
    assert len(actions) == 1
    assert actions[0]["type"] == "pause_idle_ai"

def test_native_intent_engine():
    engine = NativeIntentEngine()
    res1 = engine.detect_intent("apne skills dikhao")
    assert res1["intent"] == "self_capabilities"
    res2 = engine.detect_intent("show your skills")
    assert res2["intent"] == "self_capabilities"

def test_contradiction_engine():
    engine = ContradictionEngine()
    fact1 = {"subject": "Python", "predicate": "type", "object": "programming_language", "confidence": 0.99}
    fact2 = {"subject": "Python", "predicate": "type", "object": "snake_only", "confidence": 0.20}
    res = engine.detect_and_resolve(fact1, fact2)
    assert res["winner"]["object"] == "programming_language"
