from aiocryptopay import AioCryptoPay, Networks
from data.config import CRYPTO_PAY_TOKEN


async def cryptobot_create_invoice(currency: str, sum: float):
    crypto = AioCryptoPay(token=CRYPTO_PAY_TOKEN, network=Networks.TEST_NET)
    rates = await crypto.get_exchange_rates()
    for rate in rates:
        if rate.source == currency and rate.target == 'RUB':
            amount = sum / rate.rate
            invoice = await crypto.create_invoice(asset=currency, amount=amount)
            await crypto.close()
            return invoice
    await crypto.close()


async def check_cryptobot_invoice(invoice_id: int):
    cryptopay = AioCryptoPay(CRYPTO_PAY_TOKEN, network=Networks.TEST_NET)
    invoice = await cryptopay.get_invoices(invoice_ids=invoice_id)
    await cryptopay.close()
    if invoice.status == 'paid':
        return True
    else:
        return False
