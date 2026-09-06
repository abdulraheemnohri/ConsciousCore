import pytest
from app.core.settings_v2 import SettingsV2
from app import database

@pytest.fixture
def settings(tmp_path):
    old=database.db.path
    database.db.path=tmp_path/'settings.db'
    database.db.init()
    s=SettingsV2(); yield s
    database.db.path=old

def test_defaults_and_bounded_update(settings):
    s=settings.snapshot()
    assert s['local_only'] is True
    assert s['external_actions_require_approval'] is True
    updated=settings.update({'autonomy_level':99,'max_retrieval':0,'memory_enabled':False})
    assert updated['autonomy_level']==3
    assert updated['max_retrieval']==1
    assert updated['memory_enabled'] is False
    assert updated['immutable_safety']['auth_bypass'] is False

def test_reset(settings):
    settings.update({'learning_enabled':False})
    assert settings.reset()['learning_enabled'] is True
