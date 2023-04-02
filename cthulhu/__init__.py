from cthulhu.flask import create_app
from dotenv import load_dotenv
import os

load_dotenv()

app_settings_file = os.getenv("FLASK_APP_SETTINGS_FILE")
flask_app = create_app(app_settings_file)
