import asyncio
import uuid
from yookassa import Configuration, Payment
from config_data.config import load_config
ykassa = load_config().tg_bot.ykassa
Configuration.account_id = ykassa[0]
Configuration.secret_key = ykassa[1]


def pay(val: str, des: str):
    dict_x = {}
    payment = Payment.create({
        "amount": {
            "value": val,
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me/VPNAvocado_bot"
        },
        "capture": True,
        "description": des,
        #"target": "blank",
        "need_email": True,
        "send_email_to_provider": True,
        "receipt": {
            "customer": {
                "email": "rubazai@yandex.ru"
            },
            "items": [
            {
                "description": des,
                "quantity": 1,
                "amount": {
                    "value": val,
                    "currency": "RUB"
                },
                "vat_code": 1
            }],
        }
    }, uuid.uuid4())
    dict_x['status'] = payment.status
    dict_x['url'] = payment.confirmation.confirmation_url
    dict_x['id'] = payment.id
    print(payment.status)
    print(payment.confirmation.confirmation_url)
    return dict_x


