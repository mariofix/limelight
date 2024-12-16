import os

from dotenv import load_dotenv

from limelight import create_app

load_dotenv()

app_settings_file = os.getenv("FLASK_APP_SETTINGS_FILE")
flask_app = create_app(app_settings_file)

if __name__ == "__main__":
    flask_app.run()
