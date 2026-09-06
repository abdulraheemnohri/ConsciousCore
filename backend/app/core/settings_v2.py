from __future__ import annotations
from datetime import datetime, timezone
import json
from ..database import db

DEFAULTS={
    "local_only":True,
    "scientifically_conscious":False,
    "autonomy_level":1,
    "external_actions_require_approval":True,
    "memory_enabled":True,
    "max_working_items":32,
    "max_retrieval":8,
    "attention_enabled":True,
    "global_workspace_enabled":True,
    "reflection_enabled":True,
    "prediction_enabled":True,
    "planning_enabled":True,
    "learning_enabled":True,
    "autobiographical_memory_enabled":True,
    "event_history_limit":1000,
    "runtime_mode":"auto",
    "runtime_privacy":"private",
    "allow_cloud_llm":False,
    "allow_remote_llm":False,
    "parallel_enabled":False,
    "parallel_strategy":"judge",
    "memory_replication":"local-only",
    "cloud_memory_enabled":False,
    "remote_memory_enabled":False,
    "telemetry_enabled":False,
    "remote_telemetry_enabled":False,
}

class SettingsV2:
    """Persistent bounded runtime configuration. Safety invariants cannot be disabled here."""
    KEY="runtime_settings_v2"
    def __init__(self): self._ensure()
    def _ensure(self):
        row=db.fetchone("SELECT value FROM settings WHERE key=?",(self.KEY,))
        if not row: self._save(dict(DEFAULTS))
    def _load(self):
        row=db.fetchone("SELECT value FROM settings WHERE key=?",(self.KEY,))
        return {**DEFAULTS,**(json.loads(row["value"]) if row else {})}
    def _save(self,data):
        db.execute("INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",(self.KEY,json.dumps(data)))
    def snapshot(self):
        return {**self._load(),"updated_at":datetime.now(timezone.utc).isoformat(),"immutable_safety":{"local_only":True,"scientifically_conscious":False,"external_actions_require_approval":True,"auth_bypass":False,"secret_extraction":False,"mfa_bypass":False,"captcha_bypass":False,"secrets_remote_blocked":True}}
    def update(self,changes):
        data=self._load()
        allowed=set(DEFAULTS)-{"local_only","scientifically_conscious","external_actions_require_approval"}
        for k,v in changes.items():
            if k in allowed:
                if k=="autonomy_level": v=max(0,min(3,int(v)))
                elif k in {"max_working_items","max_retrieval","event_history_limit"}: v=max(1,min(int(v),10000))
                elif k in {"runtime_mode"}: v=str(v).lower() if str(v).lower() in {"auto","local","cloud","remote","hybrid","parallel","distributed"} else DEFAULTS[k]
                elif k in {"runtime_privacy"}: v=str(v).lower() if str(v).lower() in {"public","internal","private","sensitive","secret"} else DEFAULTS[k]
                elif k in {"parallel_strategy"}: v=str(v).lower() if str(v).lower() in {"race","judge","consensus","specialist","debate"} else DEFAULTS[k]
                elif k=="memory_replication": v=str(v).lower() if str(v).lower() in {"local-only","local+remote","local+cloud","federated"} else DEFAULTS[k]
                elif isinstance(DEFAULTS[k],bool): v=bool(v)
                data[k]=v
        self._save(data); return self.snapshot()
    def reset(self): self._save(dict(DEFAULTS)); return self.snapshot()
