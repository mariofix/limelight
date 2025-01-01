import os
from dotenv import load_dotenv
import sentry_sdk

load_dotenv()

sentry_sdk.init(
    dsn=os.getenv("FLASK_SENTRY_DSN"),
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)

from limelight import create_app


app_settings_file = os.getenv("FLASK_APP_SETTINGS_FILE")
flask_app = create_app(app_settings_file)
