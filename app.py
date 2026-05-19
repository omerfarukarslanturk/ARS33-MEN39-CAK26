from flask import Flask

from database import init_db
from routes.admin_routes import admin_bp
from routes.application_routes import application_bp
from routes.auth_routes import auth_bp
from routes.job_routes import job_bp
from routes.profile_routes import profile_bp


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-secret-key-change-in-production"

    init_db()

    app.register_blueprint(auth_bp)
    app.register_blueprint(job_bp)
    app.register_blueprint(application_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(profile_bp)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, host="127.0.0.1", port=5000)
