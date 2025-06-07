import asyncio

from datetime import datetime, timezone

from equigest.infra.session import get_session

from equigest.celery import celery_app

from equigest.services.user import (
    UserService
)


@celery_app.task
def process_billing_paid(payload):
    billing_data = payload.get('data', {}).get('billing', {})
    print(payload)
    billing_status = billing_data.get('status')
    if billing_status != "PAID":
        return

    customer_data = billing_data.get('customer', {})
    customer_id = customer_data.get('id')

    async def run():
        async for session in get_session():
            user_service = UserService(session)
            user = await user_service.get_user_by_customer_id(customer_id)
            await user_service.update_payment_status(
                user,
                datetime.now(timezone.utc),
                True
            )

    asyncio.run(run())