# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

A tiny Flask note-taking app used as a practice playground for the **Code2College Applied AI Cohort**. It's intentionally incomplete — each task in `tasks/` walks the student through fixing or adding one piece. The tests are the spec; don't edit them.

## Commands

```bash
python app.py           # run the app at http://localhost:5000
pytest                  # run all tests
pytest tests/test_task_01.py   # run a single task's tests
```

`pyproject.toml` sets `pythonpath = ["."]` so `pytest` can import `app.py` from the repo root without `python -m pytest`.

## Architecture

**Application factory.** `app.py` exports `create_app() -> Flask`. All routes are registered inside that function. The test fixtures in `tests/conftest.py` call `create_app()` directly:

```python
@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    return app

@pytest.fixture
def client(app):
    return app.test_client()
```

**In-memory note store.** Notes live in `app.notes` — an instance attribute set on the Flask app object inside `create_app()`, not a module-level global. Tests seed and clear it via the `app` fixture (`app.notes.clear()`). The store resets on every restart; there is no database.

**Templates.** `templates/new_note.html` already has:
- `value="{{ title or '' }}"` and `{{ body or '' }}` in the textarea — the view just needs to pass `title=` and `body=` back on validation failure for value-preservation to work.
- A `.error` CSS class defined and a Jinja comment placeholder marking where Task 01's error messages should appear.

`templates/home.html` iterates `notes` passed from the `home` view; Task 02's delete buttons belong inside that loop.

## Task conventions

- Tasks are in `tasks/TASK_NN.md`; their acceptance tests are in `tests/test_task_NN.py`.
- Only touch `app.py` and `templates/` — never the test files.
- Each task file lists exactly which files to change and includes hints.
- Work on a branch named `task-NN`; open a PR against `main` when tests are green.

## Key implementation hints (non-obvious)

- **Task 01 (validation):** The `new_note` route must `return render_template("new_note.html", error_title=..., error_body=..., title=title, body=body)` on failure — passing the typed values back is what makes the preservation test pass.
- **Task 02 (delete):** Declare the route with `methods=["POST"]` only; Flask automatically returns 405 for other verbs. Wrap the index lookup in `try/except IndexError: abort(404)`.
## Auth
- Never store plaintext passwords.
- ●Any config that depends on TESTING must go in a before_request hook — conftest sets it after create_app() returns.

