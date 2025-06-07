import asyncio

from datetime import datetime, timezone

from equigest.infra.session import get_session

from equigest.celery import celery_app

from equigest.services.user import (
    UserService
)

worker_loop = None

def get_worker_loop():
    global worker_loop
    if worker_loop is None or worker_loop.is_closed():
        worker_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(worker_loop)
    return worker_loop

@celery_app.task
def process_billing_paid(payload):
    billing_data = payload.get('data', {}).get('billing', {})
    billing_status = billing_data.get('status')
    if billing_status != "PAID":
        return

    customer_data = billing_data.get('customer', {})

    customer_metadata = customer_data.get('metadata', {})
    customer_name = customer_metadata.get('name', {})

    async def run():
        async for session in get_session():
            try:
                print('In Session Try-Catch')
                user_service = UserService(session)
                user = await user_service.get_user(customer_name)
                if user:
                    await user_service.update_payment_status(
                        user,
                        datetime.now(timezone.utc),
                        True
                    )
            finally:
                print('In Session Finally')
                await session.close()
                print('Session Closed With Success')
    loop = get_worker_loop()
    loop.run_until_complete(run())