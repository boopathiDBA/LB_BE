import os
import logging
import sentry_sdk
from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration
from sentry_sdk.integrations.logging import LoggingIntegration


def initialize_sentry():
    sentry_logging = LoggingIntegration(
        level=logging.DEBUG,  # Capture debug and above as breadcrumbs
        event_level=logging.ERROR  # Send errors as events
    )

    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
        integrations=[
            AwsLambdaIntegration(),
            sentry_logging,
        ],
        environment=os.getenv('DEPLOY_ENV', 'uat'),
        traces_sample_rate=0.1,
        _experiments={
            "profiles_sample_rate": 0.2,
        },
    )
