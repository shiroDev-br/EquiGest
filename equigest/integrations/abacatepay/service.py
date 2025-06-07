import requests

from fastapi import HTTPException, status

from equigest.settings import Settings

from equigest.models.user import User

settings = Settings()
ABACATEPAY_DEV_APIKEY = settings.ABACATEPAY_DEV_APIKEY

def create_billing(
    user: User
) -> dict:
    url = "https://api.abacatepay.com/v1/billing/create"

    payload = {
        "frequency": "ONE_TIME",
        "methods": ["PIX"],
        "products": [
            {
                "externalId": "prod-1",
                "name": "Assinatura do Sistema EquiGest",
                "description": "Acesso ao sistema de controle gestacional mais completo do mercado por 1 mês.",
                "quantity": 1,
                "price": 49.99
            }
        ],
        "returnUrl": "https://equigest-staging.up.railway.app/login",
        "completionUrl": "https://equigest-staging.up.railway.app/about",
        "customerId": f"customer-{user.id}",
        "customer": {
            "name":f"{user.username}",
            "cellphone": f"{user.cellphone}",
            "email": f"{user.email}",
            "taxId": f"{user.cpf_cnpj}"
        }
    }
    headers = {
        "Authorization": f"Bearer {ABACATEPAY_DEV_APIKEY}",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return {
            'billing_url': data.get("url")
        }
    else:
        raise HTTPException(
            status=status.HTTP_502_BAD_GATEWAY,
            detail='Error in billing create.'
        )