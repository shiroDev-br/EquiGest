import requests

from fastapi import HTTPException, status

from equigest.settings import Settings

from equigest.models.user import User

from equigest.integrations.abacatepay.schemas.create_customer import CreateCustomerSchema

from equigest.utils.security.cryptographer import uncrypt_fields

settings = Settings()
ABACATEPAY_DEV_APIKEY = settings.ABACATEPAY_DEV_APIKEY

class AbacatePayIntegrationService:
    def __init__(self):
        self.create_billing_url = 'https://api.abacatepay.com/v1/billing/create'
        self.create_customer_url = 'https://api.abacatepay.com/v1/customer/create'
        self.sensive_fields = ['cellphone', 'cpf_cnpj']

    def create_customer(
        self,
        customer: CreateCustomerSchema
    ) -> dict:
        payload = {
        "name": f"{customer.name}",
        "cellphone": f"{customer.cellphone}",
        "email": f"{customer.email}",
        "taxId": f"{customer.tax_id}"
        }
        headers = {
            "Authorization": f"Bearer {ABACATEPAY_DEV_APIKEY}",
            "Content-Type": "application/json"
        }

        response = requests.request("POST", self.create_customer_url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return {
                'customer_id': data['data'].get('id')
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f'Error in customer create. {response.text}'
            )

    def create_billing(
        self,
        user: User
    ) -> dict:
        uncrypt_fields(user, self.sensive_fields)

        payload = {
            "frequency": "ONE_TIME",
            "methods": ["PIX"],
            "products": [
                {
                    "externalId": "prod-1",
                    "name": "Assinatura do Sistema EquiGest",
                    "description": "Acesso ao sistema de controle gestacional mais completo do mercado por 1 mês.",
                    "quantity": 1,
                    "price": 4999
                }
            ],
            "returnUrl": "https://equigest-staging.up.railway.app/login",
            "completionUrl": "https://equigest-staging.up.railway.app/about",
            "customerId": f"{user.abacatepay_client_id}",
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

        print(payload)

        response = requests.request("POST", self.create_billing_url, json=payload, headers=headers)

        if response.status_code == 200:
            data = response.json()
            print(data)
            return {
                'billing_url': data.get("data", {}).get("url")
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f'Error in billing create. {response.text}'
            )

def get_abacatepay_integration_service() -> AbacatePayIntegrationService:
    return AbacatePayIntegrationService()