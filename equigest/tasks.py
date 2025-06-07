import requests

from fastapi import HTTPException, status

from equigest.celery import celery_app

from equigest.services.user import (
    get_user_service
)

from equigest.settings import Settings

settings = Settings()
ABACATEPAY_DEV_APIKEY = settings.ABACATEPAY_DEV_APIKEY

@celery_app.task
async def send_webhook_request():
    user_service = get_user_service()

    url = f'/payments/webhook-listener?webhookSecret={ABACATEPAY_DEV_APIKEY}'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        billing_data = data.get('data').get('billing')
        billing_status = billing_data.get('status')
        if billing_status != "PAID":
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED ,
                detail='Payment Failed.'
            )

        customer_data = billing_data.get('customer')
        customer_id = customer_data.get('id')

        user = await user_service.get_user_by_customer_id(customer_id)




