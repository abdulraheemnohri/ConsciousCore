import pytest
from app.core.world_model_v2 import WorldModelV2
from app.database import Database

@pytest.fixture
def wm(tmp_path, monkeypatch):
    database=Database(tmp_path/'world.db')
    monkeypatch.setattr('app.core.world_model_v2.db',database)
    return WorldModelV2()

def test_entity_properties_and_history(wm):
    e=wm.add_entity('a','Alpha','person',{'role':'tester'},.8)
    assert e['properties']['role']=='tester'; assert e['confidence']==.8
    wm.update_entity('a',properties={'role':'builder'},confidence=.9)
    assert len(wm.history('a'))==2

def test_temporal_relation(wm):
    r=wm.add_relation('a','supports','b',.7,valid_from='2026-01-01T00:00:00+00:00')
    assert r['confidence']==.7
    closed=wm.close_relation(r['id'],'2026-02-01T00:00:00+00:00')
    assert closed['valid_to'].startswith('2026-02')

def test_contradiction_detection(wm):
    wm.add_relation('a','is','b',.9,valid_from='2026-01-01T00:00:00+00:00')
    wm.add_relation('a','is_not','b',.6,valid_from='2026-01-02T00:00:00+00:00')
    assert len(wm.detect_contradictions())==1

def test_query_and_belief(wm):
    wm.add_entity('x','Solar Panel','device',confidence=.8)
    wm.add_belief('Solar Panel produces electricity',.75,['source-1'],'supported')
    result=wm.query('Solar')
    assert result['entities'][0]['id']=='x'; assert result['beliefs'][0]['confidence']==.75
