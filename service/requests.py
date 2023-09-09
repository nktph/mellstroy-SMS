from aiohttp import ClientSession
from data.config import SIM5_TOKEN


async def get_service_list():
    country = 'any'
    operator = 'any'

    headers = {
        'Accept': 'application/json',
    }

    pages = []

    async with ClientSession() as session:
        response = await (await session.get(url=f'https://5sim.biz/v1/guest/products/{country}/{operator}',
                                            headers=headers)).json()

        pages_count = int(len(response) / 18) + (1 if len(response) % 18 > 0 else 0)
        services = list(response.keys())
        for i in range(pages_count):
            pages.append(services[18 * i:(i + 1) * 18])

    return pages


async def get_prices(country: str, product: str):
    headers = {
        'Accept': 'application/json',
    }

    params = (
        ('country', country),
        ('product', product),
    )
    operators = []
    async with ClientSession() as session:
        try:
            resp = await (await session.get(url="https://5sim.biz/v1/guest/prices", headers=headers, params=params)).json()

            if resp:
                for operator in resp[f"{country}"][f"{product}"]:
                    if resp[f"{country}"][f"{product}"][f"{operator}"]['count'] > 0:
                        operator_data = {
                                         'name': f'{operator}',
                                         'cost': resp[f"{country}"][f"{product}"][f"{operator}"]["cost"],
                                         'count': resp[f"{country}"][f"{product}"][f"{operator}"]["count"]
                                         }
                        operators.append(operator_data)
        except Exception as e:
            print(f"Произошла ошибка при получении цен:\n\n{e}")

    return operators


async def list_order(country: str, operator: str, product: str):
    possible_errors = ['no free phones',
                       'not enough user balance',
                       'not enough rating',
                       'no product',
                       'server offline']
    headers = {
                        'Authorization': 'Bearer ' + SIM5_TOKEN,
                        'Accept': 'application/json',
                    }
    async with ClientSession() as session:
        try:
            response = await session.get(url='https://5sim.biz/v1/user/buy/activation/' + country + '/' + operator + '/' + product,headers=headers)
            resp_text = await response.text()
            print(resp_text)
            for error in possible_errors:
                if error in resp_text:
                    return error
                else:
                    response = await response.json()
                    order_data = {'id': response['id'],
                                  'phone': response['phone'],
                                  'operator': response['operator'],
                                  'product': response['product'],
                                  'country': response['country'],
                                  'price': response['price'],
                                  'status': response['status'],
                                  'sms': response['sms']}
                    return order_data
        except Exception as e:
            print(f"При покупке номера возникла ошибка: {e}")
            return " "


async def check_order(order_id: str):
    headers = {
        'Authorization': 'Bearer ' + SIM5_TOKEN,
        'Accept': 'application/json',
    }
    async with ClientSession() as session:
        response = await session.get('https://5sim.biz/v1/user/check/' + order_id, headers=headers)
        print(await response.text())
        response = await response.json()
        order_data = {'id': response['id'],
                      'phone': response['phone'],
                      'status': response['status'],
                      'sms': response['sms']}
        return order_data


async def finish_order(order_id: str):
    possible_errors = ['order not found',
                       'order expired',
                       'order no sms',
                       'hosting order']

    headers = {
        'Authorization': 'Bearer ' + SIM5_TOKEN,
        'Accept': 'application/json',
    }
    async with ClientSession() as session:
        response = await session.get('https://5sim.biz/v1/user/finish/' + order_id, headers=headers)
        print(await response.text())
        for error in possible_errors:
            if error in await response.text():
                return error
        response = await response.json()
        order_data = {'id': response['id'],
                      'phone': response['phone'],
                      'status': response['status'],
                      'sms': response['sms']}
        return order_data


async def cancel_order(order_id: str):
    possible_errors = ['order not found',
                       'order expired',
                       'order has sms',
                       'hosting order']
    headers = {
        'Authorization': 'Bearer ' + SIM5_TOKEN,
        'Accept': 'application/json',
    }
    async with ClientSession() as session:
        response = await session.get('https://5sim.biz/v1/user/cancel/' + order_id, headers=headers)
        print(await response.text())
        for error in possible_errors:
            if error in await response.text():
                return error
        response = await response.json()
        order_data = {'id': response['id'],
                      'phone': response['phone'],
                      'status': response['status'],
                      'sms': response['sms'],
                      'price': response['price']}
        return order_data
