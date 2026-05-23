"""Acceptance tests for the pinned-notes feature."""
from datetime import datetime, timezone, timedelta


def _seed(app, titles):
    app.notes.clear()
    for t in titles:
        app.notes.append({
            "title": t,
            "body": "body",
            "pinned": False,
            "pinned_at": None,
            "updated_at": datetime.now(timezone.utc),
        })


def test_pin_returns_redirect(client, app):
    _seed(app, ["A"])
    r = client.post("/notes/0/pin")
    assert r.status_code in (302, 303)


def test_pin_sets_pinned_flag(client, app):
    _seed(app, ["A"])
    client.post("/notes/0/pin")
    assert app.notes[0]["pinned"] is True
    assert app.notes[0]["pinned_at"] is not None


def test_pin_moves_note_to_top(client, app):
    _seed(app, ["First", "Second"])
    # Pin the second note (index 1)
    client.post("/notes/1/pin")
    r = client.get("/")
    body = r.data.decode()
    assert body.index("Second") < body.index("First")


def test_unpin_toggles_off(client, app):
    _seed(app, ["A"])
    client.post("/notes/0/pin")   # pin
    client.post("/notes/0/pin")   # unpin
    assert app.notes[0]["pinned"] is False
    assert app.notes[0]["pinned_at"] is None


def test_unpin_restores_order(client, app):
    # Seed two notes with distinct updated_at so order is deterministic
    app.notes.clear()
    older = datetime.now(timezone.utc) - timedelta(seconds=10)
    newer = datetime.now(timezone.utc)
    app.notes.append({"title": "Older", "body": "", "pinned": False, "pinned_at": None, "updated_at": older})
    app.notes.append({"title": "Newer", "body": "", "pinned": False, "pinned_at": None, "updated_at": newer})

    # Pin Older (index 0), confirm it moves to top
    client.post("/notes/0/pin")
    r = client.get("/")
    body = r.data.decode()
    assert body.index("Older") < body.index("Newer")

    # Unpin — Newer should be first again (higher updated_at)
    client.post("/notes/0/pin")
    r = client.get("/")
    body = r.data.decode()
    assert body.index("Newer") < body.index("Older")


def test_pin_nonexistent_returns_404(client, app):
    _seed(app, ["A"])
    r = client.post("/notes/99/pin")
    assert r.status_code == 404


def test_pin_wrong_method_returns_405(client, app):
    _seed(app, ["A"])
    r = client.get("/notes/0/pin")
    assert r.status_code == 405
