from flask import Flask
from .db import init_mongo

def create_app():
    app = Flask(__name__)

    # load .env automatically in dev (optional but nice)
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass

    init_mongo()

    from .routes import bp
    app.register_blueprint(bp)

    return app

