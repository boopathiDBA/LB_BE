import sys
import traceback
from datetime import datetime

from fastapi import Body

from app.delivery.app import get_app_and_handler
from app.repository.aladdin import *
from app.settings import SConfig
from . import router

# Using single object creation here for AWS Secrets(SConfig),
# so that object is called only one time in whole application
sconfig = SConfig()


@router.post('/update')
async def update(request: dict = Body(...)):
    queue_url = os.getenv('SQS_UPDATE_QUEUE',
                          'https://sqs.ap-southeast-2.amazonaws.com/710613906184/uat-lb-deal-update')
    if request.get("origin_store_id") and request.get("vendor_id") and request.get("source_id") and \
            request.get("request_url") and request.get("price") and request.get("in_stock"):
        payload = {
            "store_id": int(request.get("origin_store_id")),
            "vendor_id": request.get("vendor_id"),
            "sale_id": int(request.get("source_id")),
            "url": request.get("request_url"),
            "price": int(float(request.get("price")) * 100),
            "stock": int(request.get("in_stock")),
            "xpath": request.get("xpath_obj"),
            "last_update": datetime.utcnow().isoformat()
        }
        try:
            sconfig = SConfig()
            sconfig.sqs_client().send_message(QueueUrl=queue_url, MessageBody=json.dumps(payload))
            logger.info(dict(correlation_id=SConfig.correlation_id, queue_url=queue_url,
                             message="Publishing to sqs topic - on-demand-updates (xpath_obj)", payload=payload))
        except Exception as err:
            logger.error(dict(correlation_id=SConfig.correlation_id, error=err,
                              message="Error Publishing to sqs topic - on-demand-updates(xpath_obj)", payload=request))
            ex_type, ex_value, ex_traceback = sys.exc_info()
            stack_trace = []

            for trace in traceback.extract_tb(ex_traceback):
                stack_trace.append(
                    "File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            return {"Success": False, "error": stack_trace}
        return {"Success": True}
    else:
        logger.info(dict(correlation_id=SConfig.correlation_id, message="Missing field values - SQS", request=request))
        return {"Success": False, "message": "Missing field values"}


App, handler = get_app_and_handler(router)
