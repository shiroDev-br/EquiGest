import requests

import asyncio

from datetime import datetime, timezone

from equigest.infra.session import get_session

from equigest.celery import celery_app

from equigest.services.user import (
    UserService
)

from equigest.settings import Settings

settings = Settings()
ABACATEPAY_DEV_APIKEY = settings.ABACATEPAY_DEV_APIKEY

@celery_app.task
def send_webhook_request():
    async def run():
        async for session in get_session():
            user_service = UserService(session)

            url = f'http://localhost:8000/payments/webhook-listener?webhookSecret={ABACATEPAY_DEV_APIKEY}'
            print("CELERY CHAMOU EM PAI")
            response = requests.get(url)
            print(f'RESPONSE É ESSA AQUI PORRA: {response.text}')
            if response.status_code == 200:
                data = response.json()

                billing_data = data.get('data', {}).get('billing', {})
                billing_status = billing_data.get('status')
                if billing_status != "PAID":
                    print('status não tá como pago')
                    print(billing_status)
                    return

                customer_data = billing_data.get('customer', {})
                customer_id = customer_data.get('id')

                user = await user_service.get_user_by_customer_id(customer_id)
                await user_service.update_payment_status(
                    user,
                    datetime.now(timezone.utc),
                    True
                )
            else:
                print("Erro na requisição webhook:")
                print(response.status_code, response.text)

    asyncio.run(run())




