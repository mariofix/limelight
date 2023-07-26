import os

import sentry_sdk
from dotenv import load_dotenv
from sentry_sdk.integrations.flask import FlaskIntegration

from limelight import __version__, create_app

load_dotenv()

if os.environ.get("SENTRY_ENABLED", False):
    sentry_sdk.init(
        dsn=os.environ.get("SENTRY_DSN", None),
        integrations=[
            FlaskIntegration(),
        ],
        traces_sample_rate=float(os.environ.get("SENTRY_TRACE_SAMPLE_RATE", 1.0)),
        profiles_sample_rate=float(os.environ.get("SENTRY_PROFILE_SAMPLE_RATE", 1.0)),
        release=f"limelight@{__version__}",
        environment=os.environ.get("SENTRY_ENV", "production"),
        attach_stacktrace=True,
        send_default_pii=True,
    )
app_settings_file = os.getenv("FLASK_APP_SETTINGS_FILE")
flask_app = create_app(app_settings_file)

if __name__ == "__main__":
    flask_app.run()
