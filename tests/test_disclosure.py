import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from app.rules.pipeline import filter_fields

def test_unauthorised_role_excludes_everything():
    out = filter_fields(["visit_status", "estimated_arrival"], "Unauthorised", {"scheduling_updates": True})
    assert out["allowed"] == []
    assert set(out["excluded"]) == {"visit_status", "estimated_arrival"}

def test_no_consent_key_excludes_field():
    out = filter_fields(["estimated_arrival"], "Primary Contact", {"scheduling_updates": False})
    assert out["allowed"] == []
    assert "estimated_arrival" in out["excluded"]

def test_non_sensitive_field_always_allowed_for_authorised_roles():
    out = filter_fields(["some_non_sensitive_field"], "Primary Contact", {})
    assert "some_non_sensitive_field" in out["allowed"]
