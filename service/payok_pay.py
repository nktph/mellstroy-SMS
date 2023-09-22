from data.config import PAYOK_API_ID, PAYOK_API_KEY, PAYOK_SHOP_ID
from aiohttp import ClientSession


async def check_payok_payment(payment_id):
    url = f'https://payok.io/api/transaction'
    data = {'API_ID': PAYOK_API_ID, 'API_KEY': PAYOK_API_KEY, 'shop': PAYOK_SHOP_ID, 'payment': payment_id}
    async with ClientSession() as session:
        resp = (await session.post(url=url, data=data))
        response_txt = await resp.text()
        print(f"text: {response_txt}")
        if 'error' in response_txt:
            print(f"ERROR: {response_txt}")
            return 0
        else:
            resp = await resp.json(content_type="text/plain")
            transaction = resp['1']
            print(f"OK: {transaction}")
            return int(transaction['transaction_status'])