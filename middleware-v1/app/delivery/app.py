# Initializing Sentry before App initializing
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from mangum import Mangum

from app.helpers.monitoring import initialize_sentry
from app.helpers.log.router import LoggerRouteHandler
from app.helpers.config import Config
from app.helpers.log import logger
from app.settings import SConfig

# Initializing Sentry before App initializing
initialize_sentry()

# init settings
sconfig = SConfig()

# App initializing
App = FastAPI()

#Middleware
App.add_middleware(GZipMiddleware, minimum_size=1000)

origins = ["*"]

App.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
App.router.route_class = LoggerRouteHandler


# this is a mock/test service for when you start the server
# should see below response
@App.get('/')
async def index():
    # TODO: redirect to littlebirdie.com.au pre release to PROD
    return {"Hello": "Birdie"}


def get_app_and_handler(router: APIRouter):
    App.include_router(router)
    handler = None
    config = Config()

    if config.is_lambda:
        handler = Mangum(App)
        handler = logger.inject_lambda_context(handler, clear_state=True)

    return App, handler
