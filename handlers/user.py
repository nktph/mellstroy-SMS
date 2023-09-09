import decimal

from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import states
from data import *
from service import *
from database import *
# from aiogram.types import InputFile
from main import bot, dp
import keyboards
from aiogram import types


# Обработчик команды /start
@dp.message_handler(commands=['start'], state='*')
async def start_command(message: types.Message, state: FSMContext):
    await state.finish()
    user_id = message.from_user.id
    user_nickname = message.from_user.username
    referrer = None
    try:
        # Проверяем есть ли пользователь в базе
        new_user = User.create(tg_id=user_id, tg_nickname=user_nickname, balance=0, referrer=referrer)
        new_user.save()
        # Проверяем наличие хоть какой-то дополнительной информации из ссылки
        if " " in message.text:
            referrer_candidate = message.text.split()[1]

            # Пробуем преобразовать строку в число для проверки реферала
            try:
                referrer_candidate = int(referrer_candidate)
                if user_id == referrer_candidate:
                    await message.answer("Хорошая попытка, но использовать свою реферальную ссылку невозможно)")

                # Проверяем есть ли реферал в базе
                if user_id != referrer_candidate and User.select().where(User.tg_id == referrer_candidate).exists():
                    referrer = referrer_candidate
                    new_user.referrer = referrer
                    new_user.save()
                    await message.answer(text=f"Получено приглашение от пользователя "
                                              f"{User.select().where(User.tg_id == referrer).get().tg_nickname}")

            except ValueError:
                # Указана некорректная информация реферала, бонусы никому не начисляются
                pass
    except IntegrityError as e:
        pass

    await message.answer(text="👋 Приветcвую в <b>Mellstroy SMS</b>.\n🛒 Приятных покупок.",
                         reply_markup=keyboards.main_reply_menu,
                         parse_mode='html')


# Стадия покупки
@dp.callback_query_handler(state=states.StateWorker.buy)
async def purchase(call: types.CallbackQuery, state: FSMContext):
    if 'tos' in call.data:
        target_page_number = int(call.data.split(' ')[1])
        new_markup = await keyboards.get_services_kb(page=service_pages[target_page_number],
                                                     number=target_page_number,
                                                     pages_count=len(service_pages))

        await call.message.edit_reply_markup(reply_markup=new_markup)

    elif 'toc' in call.data:
        target_page_number = int(call.data.split(' ')[1])
        new_markup = await keyboards.get_countries_kb(page=countries_pages[target_page_number],
                                                      number=target_page_number,
                                                      pages_count=len(countries_pages))

        await call.message.edit_reply_markup(reply_markup=new_markup)

    elif 'service' in call.data:
        product = call.data.split(" ")[1]

        async with state.proxy() as data:
            data['product'] = product

        msg_kb_rm = await bot.send_message(chat_id=call.message.chat.id,
                                           text="aboba",
                                           reply_markup=keyboards.ReplyKeyboardRemove())
        await bot.delete_message(call.message.chat.id, msg_kb_rm.message_id)

        await call.message.edit_caption(caption=f"Выберите страну",
                                        reply_markup=await keyboards.get_countries_kb(countries_pages[0]))

    elif 'country' in call.data:
        country = call.data.split(" ")[1]
        async with state.proxy() as data:
            data['country'] = country

            operators_list = await get_prices(country=data['country'], product=data['product'])
            if not operators_list:
                await call.message.edit_caption(caption=f"Нет свободных номеров для страны {data['country'].upper()}",
                                                reply_markup=await keyboards.get_countries_kb(countries_pages[0]))
                return

        await call.message.edit_caption(caption=f"Выберите оператора",
                                        reply_markup=await keyboards.get_operators_kb(operators_list))

    elif 'oper' in call.data:
        operator = call.data.split(" ")[1]
        price = call.data.split(" ")[2]
        async with state.proxy() as data:
            data['operator'] = operator
            data['price'] = float(price)

        await call.message.edit_caption(caption=f"Ваш выбор:\n"
                                                f"Сервис: {data['product']},\n"
                                                f"Страна: {data['country']},\n"
                                                f"Оператор: {data['operator']}\n\n"
                                                f"<i><b>Итоговая стоимость: {data['price']} RUB</b></i>",
                                        parse_mode='html',
                                        reply_markup=keyboards.buy_cancel_markup)

    elif 'buy' in call.data:
        user = User.select().where(User.tg_id == call.from_user.id).get()
        async with state.proxy() as data:
            if user.balance >= data['price']:

                order_data = await list_order(country=data['country'],
                                              operator=data['operator'],
                                              product=data['product'])
                if type(order_data) is str:
                    if order_data == 'no free phones':
                        await call.message.edit_caption(
                            caption=f"Возникла ошибка при покупке: номера данного оператора закончились")
                    elif order_data == " ":
                        await call.message.edit_caption(
                            caption=f"Возникла ошибка при покупке. Повторите попытку позже.")
                    else:
                        await call.message.edit_caption(
                            caption=f"Возникла ошибка при покупке: `{order_data}`. Если данная ошибка повторяется, обратитесь в техподдержку с указанием текста ошибки",
                            parse_mode="markdown")
                else:

                    user.balance = user.balance - decimal.Decimal(data['price'])
                    user.save()
                    Order.create(user=user.tg_id,
                                 sim5_id=order_data['id'],
                                 service=order_data['product'],
                                 country=order_data['country'],
                                 operator=order_data['operator'],
                                 phone_number=order_data['phone'],
                                 price=decimal.Decimal(order_data['price']),
                                 status=order_data['status'])

                    await states.StateWorker.order_confirmation.set()
                    await call.message.edit_caption(caption=f"Покупка совершена. Ваш номер: `{order_data['phone']}`",
                                                    reply_markup=await keyboards.get_order_kb(order_id=order_data['id']),
                                                    parse_mode="markdown")
                    return
            else:
                await call.message.edit_caption(caption="Недостаточно средств")
        await state.finish()

    elif 'cancel' in call.data:
        await state.finish()
        await call.message.edit_caption(caption="Операция отменена")
        await call.message.delete()


@dp.callback_query_handler(state=states.StateWorker.order_confirmation)
async def order_confirmation(call: types.CallbackQuery, state: FSMContext):
    if 'check_order' in call.data:
        order_id = call.data.split(" ")[1]
        await call.message.edit_caption(caption="Обновление данных...")
        order_data = await check_order(order_id=order_id)
        await call.message.edit_caption(caption=f"Данные о заказе:\n\n"
                                                f"Номер: {order_data['phone']}\n"
                                                f"Статус: {statuses_ru[order_data['status']]}\n\n"
                                                f"СМС: {[sms['text'] for sms in order_data['sms']]}",
                                        reply_markup=await keyboards.get_order_kb(order_id=order_id))

    elif 'canc_order' in call.data:
        order_id = call.data.split(" ")[1]
        order_data = await cancel_order(order_id=order_id)
        if type(order_data) is str:
            if order_data == 'order has sms':
                await call.message.edit_caption(caption=f"Возникла ошибка отмене заказа: номер получил СМС",
                                                reply_markup=await keyboards.get_order_kb(order_id=order_id))
                return
            else:
                await call.message.edit_caption(caption=f"Возникла ошибка при отмене заказа: {order_data}",
                                                reply_markup=await keyboards.get_order_kb(order_id=order_id))
                return
        else:
            db_order = Order.select(Order.id, Order.sim5_id, Order.status).where(Order.sim5_id == order_id).get()
            db_order.status = order_data['status']
            db_order.save()
            user = User \
                .select(User.tg_id, User.tg_nickname, User.balance, User.referrer) \
                .where(User.tg_nickname == call.from_user.username) \
                .get()
            user.balance = user.balance + order_data['price']
            user.save()
            await state.finish()
            await states.StateWorker.buy.set()
            await call.message.edit_caption(caption=f"Заказ успешно отменён",
                                            reply_markup=await keyboards.get_services_kb(service_pages[0]))

    elif 'finish_order' in call.data:
        order_id = call.data.split(" ")[1]
        order_data = await finish_order(order_id=order_id)
        if type(order_data) is str:
            if order_data == 'order no sms':
                await call.message.edit_caption(caption=f"Возникла ошибка при закрытии заказа: номер не получал СМС.\n"
                                                        f"Если номер вам больше не нужен, рекомендуем отменить заказ.\n"
                                                        f"До получения СМС это позволит вернуть часть денег за заказ.",
                                                reply_markup=await keyboards.get_order_kb(order_id=order_id))
                return
            else:
                await call.message.edit_caption(caption=f"Возникла ошибка при закрытии заказа: {order_data}",
                                                reply_markup=await keyboards.get_order_kb(order_id=order_id))
                return
        else:
            db_order = Order.select(Order.id, Order.sim5_id, Order.status).where(Order.sim5_id == order_id).get()
            db_order.status = order_data['status']
            db_order.save()
            await state.finish()
            await states.StateWorker.buy.set()
            await call.message.edit_caption(caption=f"Заказ успешно закрыт",
                                            reply_markup=await keyboards.get_services_kb(service_pages[0]))


@dp.callback_query_handler(state=states.StateWorker.balance_method)
async def payment_method(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'cryptobot':
        await state.finish()
        await states.StateWorker.balance_currency.set()
        await call.message.edit_text("Выберите валюту", reply_markup=keyboards.currencies)


@dp.callback_query_handler(state=states.StateWorker.balance_currency)
async def cryptobot_currency(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['currency'] = call.data.upper()
    await states.StateWorker.balance_commit.set()
    await call.message.edit_text(text=f"Выбрана валюта {call.data.upper()}\n\nВведите сумму в рублях для оплаты",
                                 reply_markup=InlineKeyboardMarkup().add(keyboards.cancel))


@dp.message_handler(state=states.StateWorker.balance_commit)
async def balance_commit(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        amount = float(message.text)
        if amount < 5:
            await message.answer("Минимальная сумма перевода 5 RUB. Повторите попытку")
        else:
            async with state.proxy() as data:
                data['sum'] = amount
                invoice = await cryptobot_create_invoice(currency=data['currency'], sum=data['sum'])
                pay_btn = InlineKeyboardButton(text="Оплатить",
                                               url=invoice.pay_url)
                check_btn = InlineKeyboardButton(text="Проверить оплату",
                                                 callback_data=f"check_invoice {invoice.invoice_id}")
                await message.answer(text=f"К оплате {invoice.amount} {data['currency']}",
                                     reply_markup=InlineKeyboardMarkup(row_width=1).add(pay_btn, check_btn))

    else:
        await message.answer("Сумма перевода должна быть положительным числовым значением. Повторите ввод")


@dp.callback_query_handler(state=states.StateWorker.balance_commit)
async def check_cb_invoice(call: types.CallbackQuery, state: FSMContext):
    if 'check_invoice' in call.data:
        if await check_cryptobot_invoice(int(call.data.split(" ")[1])):
            async with state.proxy() as data:
                user = User \
                    .select(User.tg_id, User.tg_nickname, User.balance, User.referrer) \
                    .where(User.tg_nickname == call.from_user.username) \
                    .get()

                user.balance = user.balance + decimal.Decimal(data['sum'])
                user.save()

                if user.referrer:
                    print("Есть реферал")
                    referrer = User \
                        .select(User.tg_id, User.tg_nickname, User.balance, User.referrer) \
                        .where(User.tg_id == user.referrer) \
                        .get()

                    referrer.balance = referrer.balance + decimal.Decimal(data['sum'] * 0.05)
                    referrer.save()

                await call.message.edit_text(text=f"Успешно зачислено {data['sum']} RUB")
            await state.finish()
        else:
            await call.answer(text="Вы не оплатили счёт!",
                              show_alert=True)


@dp.message_handler(state=states.StateWorker.transfer)
async def transfer(message: types.Message, state: FSMContext):
    reciever_nickname = message.text.replace("@", "").strip()

    if reciever_nickname == message.from_user.username:
        await message.answer("Нельзя перевести деньги самому себе")
        await state.finish()
        return

    reciever = User.select(User.tg_id, User.tg_nickname, User.balance, User.referrer) \
        .where(User.tg_nickname == reciever_nickname)
    if reciever.exists():
        reciever = reciever.get()
        async with state.proxy() as data:
            data['reciever'] = reciever
    else:
        await message.answer("Получателя нет в базе данных", reply_markup=keyboards.main_reply_menu)
        await state.finish()
        return

    await states.StateWorker.transfer_commit.set()
    await message.answer(text=f"Получатель {reciever.tg_nickname}\nУкажите сумму перевода",
                         reply_markup=InlineKeyboardMarkup().add(keyboards.cancel))


@dp.message_handler(state=states.StateWorker.transfer_commit)
async def transfer_commit(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        transfer_sum = decimal.Decimal(message.text)
        if transfer_sum <= 0:
            await message.answer("Сумма перевода должна быть положительным числовым значением. Повторите ввод")
            return
        sender = User.select(User.tg_id, User.tg_nickname, User.balance, User.referrer) \
            .where(User.tg_id == message.from_user.id) \
            .get()
        if sender.balance >= transfer_sum:
            async with state.proxy() as data:
                reciever = data['reciever']

                sender.balance = sender.balance - transfer_sum
                sender.save()
                reciever.balance = reciever.balance + transfer_sum
                reciever.save()
                await message.answer(text=f"{transfer_sum} Успешно переведено пользователю {reciever.tg_nickname}",
                                     reply_markup=keyboards.main_reply_menu)
                await bot.send_message(chat_id=reciever.tg_id,
                                       text=f"Вам поступил перевод {transfer_sum} RUB от пользователя {sender.tg_nickname}")
                await state.finish()
        else:
            await message.answer("Недостаточно средств", reply_markup=keyboards.main_reply_menu)
            await state.finish()
    else:
        await message.answer("Сумма перевода должна быть положительным числовым значением. Повторите ввод")


@dp.message_handler(state=states.StateWorker.dialog)
async def dialog(message: types.Message, state: FSMContext):
    reply_btn = InlineKeyboardButton(text="Ответить",
                                     callback_data=f'dialog {message.from_user.id}')
    await bot.send_message(chat_id=config.SUPPORT_ID,
                           text=f"Сообщение от пользователя {message.from_user.username}\n\n*{message.text}*",
                           reply_markup=InlineKeyboardMarkup().add(reply_btn),
                           parse_mode="markdown")
    await message.answer(text="Сообщение отправлено")
    await state.finish()


@dp.message_handler(state=states.StateWorker.dialog_support_reply)
async def dialog_support_reply(message: types.Message, state: FSMContext):
    reply_btn = InlineKeyboardButton(text="Ответить",
                                     callback_data=f'dialog {message.from_user.id}')
    async with state.proxy() as data:
        await bot.send_message(chat_id=data['reciever'],
                               text=f"Сообщение от пользователя {message.from_user.username}\n\n*{message.text}*",
                               reply_markup=InlineKeyboardMarkup().add(reply_btn),
                               parse_mode="markdown")
    await message.answer(text="Сообщение отправлено")
    await state.finish()


# Главное меню
@dp.message_handler(state='*')
async def reply_handler(message: types.Message, state: FSMContext):
    await state.finish()
    if 'Купить' in message.text:

        await states.StateWorker.buy.set()
        await bot.send_photo(chat_id=message.chat.id,
                             photo="AgACAgIAAxkDAAIBRWT2XyrjhNfadEFAWpECB1hAh70kAAIh1DEblzmxS5Jp6T-hQL3HAQADAgADcwADMAQ",
                             caption="Выберите сервис",
                             reply_markup=await keyboards.get_services_kb(page=service_pages[0]))

    elif 'Профиль' in message.text:
        user = User.select(User.tg_id, User.balance).where(User.tg_id == message.from_user.id).get()
        caption_text = f"""🏦 Ваш баланс: {user.balance} RUB
🙋🏻‍♂️ Ваш id: {user.tg_id}
🛍 Кол-во покупок: {Order.select().where(Order.user == user.tg_id).count()}"""

        await bot.send_photo(chat_id=message.chat.id,
                             photo="AgACAgIAAxkDAAOFZPXIbi3N7UBmBdlCAZxfQ3K_aMUAAtjQMRuXObFLM9hdwO2K_RsBAAMCAANzAAMwBA",
                             caption=caption_text,
                             reply_markup=keyboards.account_inline_menu)

    elif 'Инфо' in message.text:
        await message.answer(text="❗️Выберите действие:", reply_markup=keyboards.info_inline_menu)


# Меню профиль/инфо
@dp.callback_query_handler(state='*')
async def account_menu(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'balance':
        await states.StateWorker.balance_method.set()
        await call.message.answer("Выберите метод оплаты", reply_markup=keyboards.pay_options_menu)

    elif call.data == 'referal':
        await call.message.answer(f"⛓️Реферальная ссылка: \n"
                                  f"`https://t.me/smsmellstr_bot/?start={call.from_user.id}`\n"
                                  f"💻 Количество рефералов: {User.select().where(User.referrer == call.from_user.id).count()}\n"
                                  f"➖➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
                                  f"Вы будете получать на баланс 5% от пополнений ваших рефералов.",
                                  parse_mode="MarkDown")
    elif call.data == 'transfer':
        await call.message.answer(
            f"*Введите ник пользователя, которому нужно отправить деньги*\n\nПожалуйста, вводите имя пользователя верно, иначе средства пропадут и возвращены не будут.",
            parse_mode="MarkDown",
            reply_markup=keyboards.ReplyKeyboardRemove())
        await states.StateWorker.transfer.set()
    elif call.data == 'history':

        orders = Order.select(Order.id, Order.service, Order.country, Order.price).where(
            Order.user == call.from_user.id)
        orders_btn = []
        for order in orders:
            orders_btn.append(InlineKeyboardButton(text=f"{order.service} - {order.country} - {order.price} RUB",
                                                   callback_data=f"order {order.id}"))
        await call.message.answer(text="История покупок",
                                  reply_markup=InlineKeyboardMarkup(row_width=1).add(*orders_btn))
    elif call.data == 'manual':
        manual_text = """<u>Инструкция использования бота:</u>

<b>1. Нажать на кнопку "Купить", выбрать необходимый сервис.</b>

<b>2. Нажать на нужный сервис, выбрать необходимую страну.</b>

<b>3. Запросить код у бота, он придет автоматически.</b> 
Если бот не выдает вам код, то значит он еще не пришел, или не был отправлен сервисом по какой-либо причине. Пример: WhatsApp не отсылает код при блокировке вашей учетной записи по железу. 

<b>4. Дождаться поступления смс и отображения его содержания.</b>
Запросить повторный код вы можете кнопку "Повторить СМС".

<b>5. Если все верно и вы хотите закончить работу с данным сервисом необходимо нажать кнопку "Активация успешна".

❗️ Максимальное время ожидания поступления СМС составляет 20 минут, после чего работа номера завершается.

‼️ Если в каком - либо сервисе не показывается нужная вам страна, значит номеров данной страны нет в наличии.</b>"""
        await call.message.answer(text=manual_text, parse_mode='html')
    elif call.data == 'rules':
        rules_text = """<u>Пользовательское соглашение:</u>

<b>1. Стоимость активаций списывается согласно прейскуранту (Отображается до покупки номера).
- 1.1 Деньги списываются с баланса по завершению операции (п.1.4,1.5 регламента).

2. Если номер выделен, но не использован (то есть вы не увидели код из смс), вы можете в любой момент отменить операцию без какого-либо штрафа.

3. При использовании данного бота вы даёте согласие на получение рекламных материалов от @smsmellstr_bot

4. Категорически запрещено использование данного сервиса @smsmellstr_bot в любых противоправных целях.
- 4.1 Также запрещено использовать данные номера с последующими целями, нарушающие Уголовный Кодекс Российской Федерации: обман, мошенничество и прочие (УК РФ 138, УК РФ 159, УК РФ 228, УК РФ 272, УК РФ 273, УК РФ 274)
- 4.2 Запрещено использование сервиса для осуществления платных подписок.

5. Мы не несем ответственности за созданные аккаунты, все действия, включая возможные блокировки, осуществляются исключительно на страх и риск конечного пользователя, который приобрел активацию.

6. Возврат денежных средств за ошибки пользователей - не предусмотрен.

7. Использование ошибок или брешей в системе безопасности запрещено и квалифицируется по УК РФ ст.273
Пользуясь данным ботом, вы подтверждаете согласие с пользовательским соглашением.

8. Сервис не делает возврат средств на QIWI кошелёк по требованию клиента. Возврат средств возможен только при форс мажорных обстоятельствах (например не работа сервиса в течение 24-ех часов, закрытие сервиса и тд.). На номер не приходит СМС, номер заблокирован в сервисе (например ВК) - не является форс-мажорным обстоятельством.

9. Запрещена покупка большого количества номеров без их использования и последующей отменой. 

10. Администрация сервиса в праве менять правила использования сервиса без оповещения пользователей.

11. Правила возврата:

Если вы ввели номер, а он оказался заблокированный до получения кода, вы должны отменить номер в боте и средства зачислятся на ваш баланс. Если код получен - номер считается использованным.

- 11.1 Возврат за номера WhatsApp производятся только при покупке номера с двухфакторной авторизацией.
Возврат при блокировке номера не предусмотрен, т.к. в большинстве случаев номер блокируется при неправильной регистрации.</b>"""
        await call.message.answer(text=rules_text, parse_mode='html')
    elif call.data == 'support':
        await states.StateWorker.dialog.set()
        await call.message.answer(
            text="_Введите сообщение для сотрудника поддержки_\n*Внимание! Не поддеживается ввод изображений. Если нужно отправить картинку, оставьте на неё ссылку.*",
            parse_mode="markdown")
    elif 'dialog' in call.data:
        async with state.proxy() as data:
            data['reciever'] = call.data.split(" ")[1]
        await call.message.answer(
            text="Введите ответ\n\n*Внимание! Не поддеживается ввод изображений. Если нужно отправить картинку, оставьте на неё ссылку.*",
            parse_mode="markdown")
        await states.StateWorker.dialog_support_reply.set()
    elif 'cancel' in call.data:
        await state.finish()
        await call.message.answer(text="Операция отменена", reply_markup=keyboards.main_reply_menu)
        await call.message.delete()

    # else:
    #     await call.message.answer(text="Чё?")
