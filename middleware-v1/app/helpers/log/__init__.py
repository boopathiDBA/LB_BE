import os
from aws_lambda_powertools import Logger

date_format = "%Y-%m-%dT%H:%M:%S.%f%z"

logger: Logger = Logger(datefmt=date_format)
