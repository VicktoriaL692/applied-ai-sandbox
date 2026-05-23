"""Tiny Flask app — applied-ai-sandbox.

Each task in tasks/ asks you to add or fix one piece. The tests in tests/
describe exactly what "done" means.
"""
from __future__ import annotations

from flask import Flask, render_template, request, redirect, url_for
from flask_login import login_required, login_user, logout_user, current_user

from models import db, login_manager, User


def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "sandbox-not-a-real-secret"
    # Default: in-memory SQLite (tests and quick runs). Override via config param.
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
    if config:
        app.config.update(config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "login"

    # LOGIN_DISABLED must be set at request time because conftest sets TESTING
    # after create_app() returns. Flask-Login checks this key per request.
    @app.before_request
    def _maybe_disable_login():
        if app.testing:
            app.config["LOGIN_DISABLED"] = True

    @login_manager.user_loader
    def load_user(user_id: str):
        return db.session.get(User, int(user_id))

    # In-memory store for the sandbox. Resets on every restart, which is
    # fine for practice. Real apps use a database.
    app.notes: list[dict] = []  # type: ignore[attr-defined]

    # --- auth routes ---

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for("home"))
        error = None
        if request.method == "POST":
            username = (request.form.get("username") or "").strip()
            password = request.form.get("password") or ""
            if not username or not password:
                error = "Username and password are required."
            elif User.query.filter_by(username=username).first():
                error = "Username already taken."
            else:
                user = User(username=username)
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
                login_user(user)
                return redirect(url_for("home"))
        return render_template("register.html", error=error)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("home"))
        error = None
        if request.method == "POST":
            username = (request.form.get("username") or "").strip()
            password = request.form.get("password") or ""
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user)
                return redirect(url_for("home"))
            error = "Invalid username or password."
        return render_template("login.html", error=error)

    @app.route("/logout", methods=["POST"])
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("login"))

    # --- note routes ---

    @app.route("/")
    @login_required
    def home():
        if current_user.is_authenticated:
            notes = [n for n in app.notes if n.get("user_id") == current_user.id]
        else:
            notes = app.notes
        return render_template("home.html", notes=notes)

    @app.route("/notes/new", methods=["GET", "POST"])
    @login_required
    def new_note():
        if request.method == "POST":
            title = (request.form.get("title") or "").strip()
            body = (request.form.get("body") or "").strip()
            tags_raw = request.form.get("tags") or ""
            tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
            title_error = "Title is required" if not title else None
            body_error = "Body is required" if not body else None
            if title_error or body_error:
                return render_template(
                    "new_note.html",
                    title=title,
                    body=body,
                    tags=tags_raw,
                    title_error=title_error,
                    body_error=body_error,
                )
            note = {"title": title, "body": body, "tags": tags}
            if current_user.is_authenticated:
                note["user_id"] = current_user.id
            app.notes.append(note)
            return redirect(url_for("home"))
        return render_template("new_note.html")

    # TASK 02 will add a /notes/<idx>/delete route here.

    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    create_app({"SQLALCHEMY_DATABASE_URI": "sqlite:///users.db"}).run(
        debug=True, port=5000
    )
