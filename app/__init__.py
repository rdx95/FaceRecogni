from flask import Flask

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="https://574cb4b827c142d09b6636a6d9d25bbf@sentry.io/5174169",
    integrations=[FlaskIntegration()]
)

app = Flask(__name__)

from app import FaceRecogni
from app import view