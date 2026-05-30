# EcoParking API documentation

- Default content type: [application/json](https://www.iana.org/assignments/media-types/application/json)

EcoParking API для мобильного и веб приложения пользователей электрических станций зарядок.

## О документации

**PUB** - это publish, то есть это описание сообщений, которые можно отправлять на сервер. По сути это запросы. Но в
ответ может прийти несколько сообщений.

**SUB** - это subscripbe, то есть то, что может прийти с сервера.

Все сообщения оборачиваются в Конверты:

| Name | Type           | Description    | Notes                                                                                    |
|------|----------------|----------------|------------------------------------------------------------------------------------------|
| type | `string`       | Тип сообщения  | Все типы будут описаны далее, например `init`, `sessions_history`, `phone_auth_response` |
| data | `object\|list` | Тело сообщения | Это полезная нагрузка. У каждого типа сообщения своя схема этого объекта                 |

Тип сообщения будет записан, как имя `PUB $type` или `SUB $type`. Например, `PUB sessions_history` — это сообщение
вида `{"type": "sessions_history", "data": {}}`.

TODO: формат ошибки

## Servers

### `production` Server

- URL: `api.eco-nrg.store/ws/socket-server/`
- Protocol: `wss`

### `staging` Server

- URL: `api.eco-parking.7bits.it/ws/socket-server/`
- Protocol: `wss`

[[_TOC_]]

## PUB `init`

Аутентификация по токену.

В данный момент Токен - это просто строка, не JWT. В будущем перейдем на JWT.

| Name  | Type     | Description        | Notes                                                          |
|-------|----------|--------------------|----------------------------------------------------------------|
| token | `string` | Токен пользователя | Токен можно получить с помощью [`phone_auth`](#pub-phone_auth) |

> Пример сообщения

```json
{
  "type": "init",
  "data": {
    "token": "97fa11e367646ccc18114b0fc152f04c1798d45"
  }
}
```

В ответ всегда приходят:

- [profile_response](#sub-profile_response)
- [phone_auth_response](#sub-phone_auth_response)
- [refill_response](#sub-refill_response)
- [map_response](#sub-map_response)
- [sessions_history_response](#sub-sessions_history_response)

Если есть активная сессия зарядки, то приходит еще [session_charging](#sub-session_charging)

## PUB `phone_auth`

Аутентификация по номеру телефона и коду

| Name  | Type     | Description                                                                        | Notes |
|-------|----------|------------------------------------------------------------------------------------|-------|
| phone | `string` | Номер телефона в формате `79998887766` без `+` и с `7` в начале                    |       |
| code  | `string` | Код из 6 символов, которые отправляется по СМС при [регистрации](#pub-phone_check) |       |

> Пример сообщения

```json
{
  "type": "phone_auth",
  "data": {
    "phone": "79998887766",
    "code": "123456"
  }
}
```

В ответ приходит тоже самое, что и для [init](#pub-init)

## PUB `phone_check`

Проверить зарегистрирован ли номер телефона в системе. Если нет, тогда автоматическая регистрация: на телефон придет СМС
с кодом для входа.

| Name  | Type     | Description                                                     | Notes |
|-------|----------|-----------------------------------------------------------------|-------|
| phone | `string` | Номер телефона в формате `79998887766` без `+` и с `7` в начале |       |

> Пример сообщения

```json
{
  "type": "phone_check",
  "data": {
    "phone": "79998887766"
  }
}
```

В ответ приходит [phone_check_response](#sub-phone_check_response)

## PUB `send_code`

Запросить новый пароль по СМС

| Name  | Type     | Description                                                     | Notes |
|-------|----------|-----------------------------------------------------------------|-------|
| phone | `string` | Номер телефона в формате `79998887766` без `+` и с `7` в начале |       |

> Пример сообщения

```json
{
  "type": "phone_check",
  "data": {
    "phone": "79998887766"
  }
}
```

В ответ приходит [send_code_response](#sub-send_code_response)

## PUB `logout`

Аннулировать токен аутентификации

> Пример сообщения

```json
{
  "type": "logout"
}
```

В ответ приходит ничего. Данная сокет сессия больше не ассоциирована с пользователем.

## PUB `edit_profile`

Редактирование профиля пользователя

| Name         | Type     | Description     | Notes                                                   |
|--------------|----------|-----------------|---------------------------------------------------------|
| first_name   | `string` | Имя             |                                                         |
| middle_name  | `string` | Отчество        |                                                         |
| manufacturer | `string` | Марка машины    |                                                         |
| model        | `string` | Модель машин    | Список моделей есть в `profile_response.data.listModel` |
| number       | `string` | Номер машины    |                                                         |
| year         | `string` | Год выпуска     |                                                         |
| power        | `string` | Емкость батареи |                                                         |
| fast_type    | `string` | Быстрый тип     | `CHADEMO, CCS-Combo1, CCS-Combo2, GB-T`                 |
| slow_type    | `string` | Медленный тип   | `J1772, IEC62196, TESLA_US`                             |

> Пример сообщения

```json
{
  "type": "edit_profile",
  "data": {
    "phone": "79998887766",
    "first_name": "Иван",
    "middle_name": "Иванович",
    "manufacturer": "BAIC",
    "model": "EU5",
    "number": "а777аа",
    "year": 2000,
    "power": 6,
    "fast_type": "GB-T",
    "slow_type": "TESLA_US"
  }
}
```

В ответ приходит

## PUB `refill`

Запросить все зарядные станции

| Name | Type | Description | Notes |
|------|------|-------------|-------|

> Пример сообщения

```json
{
  "type": "refill"
}
```

В ответ приходит

## PUB `start_session`

Активация зарядной станции

| Name  | Type     | Description         | Notes                                  |
|-------|----------|---------------------|----------------------------------------|
| id    | `string` | ID зарядной станции | на которой активировали сессию зарядки |
| type  | `string` | Тип коннектора      |                                        |
| token | `string` | Токен пользователя  | Не используется                        |

> Пример сообщения

```json
{
  "type": "start_session",
  "data": {
    "id": "2",
    "type": "TES_US",
    "token": "07ff10e387646ccc1854f4b0fc152f04c1798d43"
  }
}
```

В ответ приходит:

- [start_session_success](#sub-start_session_success)
- [session_charging](#sub-session_charging) (приходит не сразу, с задержкой в 5 секунд. И потом периодически приходит до
  тех пор, пока идет зарядка)
- [refill_response](#sub-refill_response)
- [sessions_history_response](#sub-sessions_history_response)

## PUB `stop_session`

Завершение текущей активной зарядки

| Name  | Type     | Description        | Notes                                          |
|-------|----------|--------------------|------------------------------------------------|
| token | `string` | Токен пользователя | Тут его не должно быть. Видимо не используется |

> Пример сообщения

```json
{
  "type": "stop_session",
  "data": {
    "token": "07ff10e387646ccc1854f4b0fc152f04c1798d43"
  }
}
```

В ответ приходит:

- session_stop
- phone_auth_response
- sessions_history_response
- refill_response

## PUB `sessions_history`

Запросить историю заказов.

Секция `data` не используется пока что.

> Пример сообщения

```json
{
  "type": "sessions_history"
}
```

В ответ приходит: [sessions_history_response](#sub-sessions_history_response)

## PUB `session_chart`

Запросить данные для графика потребления электроэнергии: кВт и Ампер

| Name       | Type   | Description       | Notes                                                                                   |
|------------|--------|-------------------|-----------------------------------------------------------------------------------------|
| order_uuid | UUIDv4 | ID сессии зарядки | Взять из [`sessions_history_response.data[#].uuid`](<(#sub-sessions_history_response)>) |

> Пример сообщения

```json
{
  "type": "session_chart",
  "data": {
    "order_uuid": "4b69e2d6-139a-463a-9c6b-5ff8e3bf38c3"
  }
}
```

В ответ приходит [`session_chart_response`](#sub-session_chart_response)

## PUB `book_space`

Забронировать зарядную станцию

| Name           | Type     | Description         | Notes                                  |
|----------------|----------|---------------------|----------------------------------------|
| space_id       | `string` | ID зарядной станции | на которой активировали сессию зарядки |
| connector_type | `string` | Тип коннектора      |                                        |

> Пример сообщения

```json
{
  "type": "book_space",
  "data": {
    "space_id": 5,
    "connector_type": "TES_US"
  }
}
```

В ответ приходит:

- [`book_space_response`](#sub-book_space_response)
- [`refill_response`](#sub-refill_response)
- [`phone_auth_response`](#sub-phone_auth_response)

Могут прийти ошибки [type:error_response](#sub-error_response). Некоторые из них:

- Можно бронировать только одну станцию
- Профиль должен быть заполнен, чтобы забронировать место
- Недостаточно бесплатного времени для бронирования на 1 час
- Можно бронировать только одну станцию
- В день можно бронировать один раз
- Парковочное место не найдено
- Парковочное место забронированно
- Парковочное место выключено
- Парковочное место занято
- Парковочное место недоступно
- Коннектор не найден

## PUB `get_booking`

Запросить текущее бронирование у пользователя.

> Пример сообщения

```json
{
  "type": "get_booking"
}
```

В ответ приходит:

- [`book_space_response`](#sub-book_space_response)

## PUB `cancel_bookings`

Отмена всех активных бронирований пользователя.
TODO: в данный момент у пользователя может быть только одно бронирование!

> Пример сообщения

```json
{
  "type": "cancel_bookings"
}
```

В ответ приходит:

- [`cancel_bookings_response`](#sub-cancel_bookings_response)
- [`refill_response`](#sub-refill_response)
- [`phone_auth_response`](#sub-phone_auth_response)

## PUB `get_payments`

Запросить платежи.

| Name            | Type     | Description      | Notes      |
|-----------------|----------|------------------|------------|
| page_number     | `number` | Номер страницы   |            |
| page_size       | `number` | Размер страницы  |            |
| order_direction | `string` | `"desc"\| "asc"` | Сортировка |

> Пример сообщения

```json
{
  "type": "get_payments",
  "data": {
    "page_number": 2,
    "page_size": 1,
    "order_direction": "desc"
  }
}
```

В ответ приходит: [`get_payments_response`](#sub-get_payments_response)

## PUB `create_payment_url`

Запросить ссылку для оплаты. В запросе передаем,
сколько рублей хочет заплатить человек, эта информация будет
зашита в итоговой ссылке

> Пример сообщения

```json
{
  "type": "create_payment_url",
  "data": {
    "amount": 100
  }
}
```

В ответ приходит: [`payment_url_response`](#sub-payment_url_response)

## PUB `convert_bonuses`

Конвертация бонусов в рубли по курсу 1 к 1.

Если бонусы невозможно конвертировать, тогда придет [`error_response`](#sub-error_response).

> Пример сообщения

```json
{
  "type": "convert_bonuses",
  "data": {
    "amount": 100
  }
}
```

В ответ приходят:

- [`convert_bonuses_response`](#sub-convert_bonuses_response)
- [`phone_auth_response`](#sub-phone_auth_response) (с новым состоянием баланса и бонусов)

## SUB `phone_check_response`

| Name     | Type      | Description                                                                                                             | Notes |
|----------|-----------|-------------------------------------------------------------------------------------------------------------------------|-------|
| detail   | `string?` | "СМС успешно отправлено" или ничего                                                                                     |       |
| new_user | `bool`    | Если юзер новый, то `true`, иначе `false`. Новому пользователю сразу создадут профиль. И отправят СМС с кодов для входа |       |

> Пример сообщения

```json
{
  "type": "phone_check_response",
  "data": {
    "detail": "СМС успешно отправлено",
    "new_user": true
  }
}
```

```json
{
  "type": "phone_check_response",
  "data": {
    "new_user": false
  }
}
```

## SUB `phone_auth_response`

| Name                        | Type           | Description                                             | Notes                                                                                                                                        |
|-----------------------------|----------------|---------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------|
| auth                        | `string`       | Токен авторизации, который использует [init](#pub-init) |                                                                                                                                              |
| cashData                    | `object`       | Данные Лицевого счета пользователя                      |                                                                                                                                              |
| cashData.money              | `number`       | ?                                                       | Не используется                                                                                                                              |
| cashData.bonus              | `number`       | ?                                                       | Не используется                                                                                                                              |
| cashData.freeTime           | `number`       | Бесплатные минуты                                       | Каждый сутки пользователю выдается 5 часов для зарядки. Когда у него нет бесплатного времени, то он не может заряжать и бронировать станцию. |
| book_state                  | `string\|null` | уведомление об освобождении станции                     | Не используется                                                                                                                              |
| bonusUser                   | `object[]`     | Список бонусов                                          | Не используется                                                                                                                              |
| bonusUser[#].command        | `string`       | ?                                                       | Не используется                                                                                                                              |
| bonusUser[#].summ           | `number`       | ?                                                       | Не используется                                                                                                                              |
| alertMessanger              | `object[]`     | Список предупреждений для пользователя                  |                                                                                                                                              |
| alertMessanger[#].page      | `string`       | ?                                                       |                                                                                                                                              |
| alertMessanger[#].command   | `string`       | Что надо сделать пользователю                           | Например: `fill_profile`                                                                                                                     |
| alertMessanger[#].icon      | `string`       | ?                                                       |                                                                                                                                              |
| alertMessanger[#].messanger | `string`       | Текст уведомления                                       | Например, "Заполните профиль чтобы получать скидки и бонусы"                                                                                 |

> Пример сообщения

```json
{
  "type": "phone_auth_response",
  "data": {
    "auth": "97fa11e367646ccc18114b0fc152f04c1798d45",
    "cashData": {
      "money": 0.0,
      "bonus": 300.0,
      "freeTime": 17925
    },
    "book_state": null,
    "bonusUser": [
      {
        "command": "new_user",
        "summ": 100
      },
      {
        "command": "fill_profile",
        "summ": 200
      }
    ],
    "alertMessanger": []
  }
}
```

```json
{
  "type": "phone_auth_response",
  "data": {
    "auth": "97fa11e367646ccc18114b0fc152f04c1798d45",
    "cashData": {
      "money": 0.0,
      "bonus": 100.0,
      "freeTime": 18000
    },
    "book_state": null,
    "bonusUser": [
      {
        "command": "new_user",
        "summ": 100
      }
    ],
    "alertMessanger": [
      {
        "page": "profile",
        "command": "fill_profile",
        "icon": "exclamation",
        "messanger": "Заполните профиль чтобы получать скидки и бонусы"
      }
    ]
  }
}
```

## SUB `send_code_response`

| Name    | Type     | Description                          | Notes                                                             |
|---------|----------|--------------------------------------|-------------------------------------------------------------------|
| message | `string` | Результат запроса                    | Если все хорошо, то "СМС отправлено". Иначе придет error_response |
| success | `bool`   | В случае успеха `true` иначе `false` |                                                                   |

> Пример сообщения

```json
{
  "type": "send_code_response",
  "data": {
    "message": "СМС отправлено",
    "success": true
  }
}
```

> Пример сообщения с ошибкой

```json
{
  "type": "error_response",
  "data": {
    "message": "Слишком частая отправка. Попробуйте позже",
    "request": "send_code"
  }
}
```

## SUB `profile_response`

| Name | Type | Description | Notes |
|------|------|-------------|-------|
| name | type | description | notes |

> Пример сообщения

```json
{
  "profileData": {
            "phone": "8 (000) 000-00-00",
            "email": user.profile.email,
            "first_name": user.profile.first_name,
            "middle_name": user.profile.middle_name,
        },
        "carData": {
            "manufacturer": user.profile.car_manufacturer,
            "model": user.profile.car_model,
            "number": user.profile.car_number,
            "year": user.profile.car_year,
        },
        "batteryData": {
            "power": ,
            "fast_type": user.profile.fast_type,
            "slow_type": user.profile.slow_type,
        },
        "listModel": car_keys,
        "listModelAll": car_list,
        "listManufacturer": [
            {
                "value": "x",
                "selected": x == user.profile.car_manufacturer,
            }
        ],
        "fast_choices": dict(Profile.FAST_CHOICES),
        "slow_choices": dict(Profile.SLOW_CHOICES),
        "filledProfile": true
}
```

## SUB `edit_profile_response`

| Name | Type | Description | Notes |
|------|------|-------------|-------|
| name | type | description | notes |

> Пример сообщения

```json
{}
```

## SUB `refill_response`

Приходит массив объектов:

- города
    - парковки
        - парковочные места (станции)

| Name                                                          | Type                     | Description                                       | Notes                                                                                    |
|---------------------------------------------------------------|--------------------------|---------------------------------------------------|------------------------------------------------------------------------------------------|
| `name`                                                        | string                   | Город                                             |                                                                                          |
| `station`                                                     | object[]                 | Список парковок                                   |                                                                                          |
| `station[#].id`                                               | number                   | ID парковки                                       |                                                                                          |
| `station[#].name`                                             | string                   | Название парковки                                 |                                                                                          |
| `station[#].img`                                              | string                   |                                                   |                                                                                          |
| `station[#].img_map`                                          | string                   |                                                   |                                                                                          |
| `station[#].img_cam`                                          | string                   |                                                   |                                                                                          |
| `station[#].address`                                          | string                   | Адрес парковки                                    | дублируется с именем                                                                     |
| `station[#].show`                                             | bool                     |                                                   | Не используется                                                                          |
| `station[#].spaces`                                           | object[]                 | Список парковочных мест (станций)                 |                                                                                          |
| `station[#].spaces[#].id`                                     | number                   | ID парковочного места                             |                                                                                          |
| `station[#].spaces[#].name`                                   | string                   | Название места                                    |                                                                                          |
| `station[#].spaces[#].status`                                 | `"AW"\|"BU"\|"DI"\|"BO"` | Статус места                                      | Доступно для зарядки, занято, выключено, забронировано                                   |
| `station[#].spaces[#].booked_until`                           | `number\|null`           | До какого времени забронировано парковочное место | Если станция не забронирована, то null                                                   |
| `station[#].spaces[#].price_kwh`                              | number                   | Стоимость кВт/ч                                   |                                                                                          |
| `station[#].spaces[#].price_parking`                          | number                   | Стоимость простоя (парковка без зарядки)          |                                                                                          |
| `station[#].spaces[#].connectors`                             | object[]                 | Список коннекторов                                |                                                                                          |
| `station[#].spaces[#].connectors[#].type`                     | string                   | Название типа коннектора                          |                                                                                          |
| `station[#].spaces[#].connectors[#].phases_count`             | number                   | Количество фаз                                    |                                                                                          |
| `station[#].spaces[#].connectors[#].current_a`                | number                   |                                                   |                                                                                          |
| `station[#].spaces[#].connectors[#].power_kw`                 | number                   |                                                   |                                                                                          |
| `providers`                                                   | object                   | Словарь провайдеров услуг этой станции.           | `PROVIDING` - Организация предоставляющая услуги. `SERVICE` - Обслуживающая организация. |
| `providers['PROVIDING' \| 'SERVICE']`                         | object                   | Данные компании по типу                           |                                                                                          |
| `providers['PROVIDING' \| 'SERVICE'].name`                    | string                   | Название компании                                 |                                                                                          |
| `providers['PROVIDING' \| 'SERVICE'].address`                 | string                   | Юридический и фактический адрес                   |                                                                                          |
| `providers['PROVIDING' \| 'SERVICE'].ogrn`                    | string                   | ОГРН                                              |                                                                                          |
| `providers['PROVIDING' \| 'SERVICE'].inn`                     | string                   | ИНН                                               |                                                                                          |
| `providers['PROVIDING' \| 'SERVICE'].kpp`                     | string                   | КПП                                               |                                                                                          |
| `providers['PROVIDING' \| 'SERVICE'].payment_account`         | string                   | Расчетный счёт                                    |                                                                                          |
| `providers['PROVIDING' \| 'SERVICE'].branch_office`           | string                   | Филиал банка                                      |                                                                                          |
| `providers['PROVIDING' \| 'SERVICE'].pao`                     | string                   | Название банка                                    |                                                                                          |
| `providers['PROVIDING' \| 'SERVICE'].bik`                     | string                   | БИК                                               |                                                                                          |
| `providers['PROVIDING' \| 'SERVICE'].correspondent_account`   | string                   | Корреспондентский счет                            |                                                                                          |
| `providers['PROVIDING' \| 'SERVICE'].extra_information`       | object                   | Дополнительная контактная информация              |                                                                                          |
| `providers['PROVIDING' \| 'SERVICE'].extra_information.email` | string                   | Почта                                             |                                                                                          |
| `providers['PROVIDING' \| 'SERVICE'].extra_information.phone` | string[]                 | Массив номеров                                    |                                                                                          |

> Пример сообщения

```json
{
  "type": "refill_response",
  "data": [
    {
      "name": "Краснодар",
      "station": [
        {
          "id": 1,
          "name": "Конгрессная 31к1",
          "img": "https://api.eco-nrg.store/media/camera/image_3/246.jpg?t=1687267702.0",
          "img_map": "https://api.eco-nrg.store/media/map/1.png",
          "img_cam": "https://api.eco-nrg.store/media/camera/image_3/246.jpg?t=1687267702.0",
          "address": "Конгрессная 31к1",
          "show": false,
          "providers": {
            "PROVIDING": [
              {
                "name": "«ЭКО-ЭНЕРГО»",
                "address": "350020, Краснодарский край, г Краснодар, ул Коммунаров, д. 221/1, офис 16",
                "ogrn": "1111111111111",
                "inn": "2222222222",
                "kpp": "333333333",
                "payment_account": "",
                "branch_office": "",
                "pao": "",
                "bik": "",
                "correspondent_account": "",
                "extra_information": {
                  "email": "info@eco-nrg.store",
                  "phone": [
                    "8 (000) 000-00-00",
                    "8 (111) 000-00-00"
                  ]
                }
              }
            ],
            "SERVICE": [
              {
                "name": "«РКС» (ООО «РКС»)",
                "address": "350020, Краснодарский край, г. Краснодар, ул. Коммунаров, д. 221/1, пом. 10",
                "ogrn": "1111111111111",
                "inn": "2222222222",
                "kpp": "333333333",
                "payment_account": "55555555555555555555",
                "branch_office": "Ростовский",
                "pao": "Альфа-Банк",
                "bik": "00000000",
                "correspondent_account": "9999999999999999999",
                "extra_information": {}
              }
            ]
          },
          "spaces": [
            {
              "id": 3,
              "name": "003",
              "status": "AW",
              "price_kwh": 10.0,
              "price_parking": 100.0,
              "connectors": [
                {
                  "type": "J1772",
                  "phases_count": 1,
                  "current_a": 48.0,
                  "power_kw": 12.0
                }
              ]
            },
            {
              "id": 2,
              "name": "002",
              "status": "AW",
              "price_kwh": 10.0,
              "price_parking": 100.0,
              "connectors": [
                {
                  "type": "TES_US",
                  "phases_count": 1,
                  "current_a": 80.0,
                  "power_kw": 20.0
                }
              ]
            },
            {
              "id": 1,
              "name": "001",
              "status": "AW",
              "price_kwh": 10.0,
              "price_parking": 100.0,
              "connectors": [
                {
                  "type": "IEC_62196",
                  "phases_count": 3,
                  "current_a": 32.0,
                  "power_kw": 22.0
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

## SUB `start_session_success`

Сообщение приходит когда сессия зарядки началась успешно.

| Name            | Type     | Description                               | Notes                     |
|-----------------|----------|-------------------------------------------|---------------------------|
| id              | `string` | ID зарядной станции                       |                           |
| connector_type  | `string` | Тип коннектора                            | Например, J1772           |
| created_at      | `string` | Дата активации зарядной станции           |                           |
| start_payed     | `string` | Дата начала платной зарядки               |                           |
| cash            | `string` | Сколько потрачено денег за эту сессию     |                           |
| total_kwh       | `string` | Потреблено электроэнергии ВСЕГО: кВт      |                           |
| am              | `string` | Текущее показание потребление тока, Ампер |                           |
| current_kwh     | `string` | Текущее показание потребления, кВт        |                           |
| current_v       | `string` | Текущее показание потребления, Воль       |                           |
| selected_camera | `string` | Всегда 1                                  | Используется на фронтенде |
| cam_1           | `string` | Первая камера                             | Общий вид                 |
| cam_2           | `string` | Вторая камера                             | Вид на машину             |

> Пример сообщения

```json
{
  "type": "start_session_success",
  "data": {
    "id": 2,
    "connector_type": "TES_US",
    "created_at": 1687333918000,
    "start_payed": null,
    "cash": 0.0,
    "total_kwh": 0.0,
    "am": 0.0,
    "current_kwh": 0.0,
    "current_v": 239.33,
    "selected_camera": 1,
    "cam_1": "https://api.eco-nrg.store/media/camera/image_3/124.jpg?t=1687333922.0",
    "cam_2": "https://api.eco-nrg.store/media/camera/image_2/174.jpg?t=1687333919.0"
  }
}
```

## SUB `session_charging`

Сообщение приходит каждую 5-10ую секунду с сервера, если есть активная зарядка. С такой скоростью зарядная станция
отправляет данные (показатели счетчика) на сервер, которые рассылаются уже пользователям.

| Name            | Type     | Description                               | Notes                     |
|-----------------|----------|-------------------------------------------|---------------------------|
| id              | `string` | ID зарядной станции                       |                           |
| connector_type  | `string` | Тип коннектора                            | Например, J1772           |
| created_at      | `string` | Дата активации зарядной станции           |                           |
| start_payed     | `string` | Дата начала платной зарядки               |                           |
| cash            | `string` | Сколько потрачено денег за эту сессию     |                           |
| total_kwh       | `string` | Потреблено электроэнергии ВСЕГО: кВт      |                           |
| am              | `string` | Текущее показание потребление тока, Ампер |                           |
| current_kwh     | `string` | Текущее показание потребления, кВт        |                           |
| current_v       | `string` | Текущее показание потребления, Воль       |                           |
| selected_camera | `string` | Всегда 1                                  | Используется на фронтенде |
| cam_1           | `string` | Первая камера                             | Общий вид                 |
| cam_2           | `string` | Вторая камера                             | Вид на машину             |

> Пример сообщения

```json
{
  "type": "session_charging",
  "data": {
    "id": 2,
    "connector_type": "TES_US",
    "created_at": 1687333918000,
    "start_payed": null,
    "cash": 0.0,
    "total_kwh": 0.0,
    "am": 0.0,
    "current_kwh": 0.0,
    "current_v": 239.33,
    "selected_camera": 1,
    "cam_1": "https://api.eco-nrg.store/media/camera/image_3/124.jpg?t=1687333922.0",
    "cam_2": "https://api.eco-nrg.store/media/camera/image_2/174.jpg?t=1687333919.0"
  }
}
```

## SUB `session_stop`

Сообщение о том, что на завершилась сессия зарядки.

| Name | Type     | Description         | Notes                     |
|------|----------|---------------------|---------------------------|
| id   | `number` | ID зарядной станции | Которая закончила зарядку |

> Пример сообщения

```json
{
  "type": "session_stop",
  "data": {
    "id": 2
  }
}
```

## SUB `map_response`

Список зарядных станций с координатами.

TODO: координаты надо перенести в [refill_response](#sub-refill_response) скорее всего.

| Name             | Type      | Description                        | Notes                        |
|------------------|-----------|------------------------------------|------------------------------|
| markers          | object[]  | Список маркеров                    | Каждый маркер — это парковка |
| markers[#].coord | number[2] | Координаты маркера. Всегда 2 числа |                              |

> Пример сообщения

```json
{
  "type": "map_response",
  "data": {
    "config": {
      "coords": [
        45.10824969947851,
        38.95658311079924
      ],
      "zoom": 17,
      "iconImageSize": [
        30,
        50
      ]
    },
    "markers": [
      {
        "index": 2,
        "name": "Уральская 138",
        "address": "ул. Уральская 138",
        "coord": [
          45.03696704647179,
          39.07927856973962
        ],
        "zoom": 17,
        "spaces": [
          {
            "id": 4,
            "status": "DI",
            "connectors": [
              {
                "type": "IEC_62196",
                "phases_count": 3,
                "current_a": 32.0,
                "power_kw": 22.0
              }
            ]
          }
        ]
      },
      {
        "index": 1,
        "name": "Конгрессная 31к1",
        "address": "ул. Конгрессная 31к1",
        "coord": [
          45.10824969947851,
          38.95658311079924
        ],
        "zoom": 16,
        "spaces": [
          {
            "id": 3,
            "status": "AW",
            "connectors": [
              {
                "type": "J1772",
                "phases_count": 1,
                "current_a": 48.0,
                "power_kw": 12.0
              }
            ]
          },
          {
            "id": 2,
            "status": "AW",
            "connectors": [
              {
                "type": "TES_US",
                "phases_count": 1,
                "current_a": 80.0,
                "power_kw": 20.0
              }
            ]
          },
          {
            "id": 1,
            "status": "AW",
            "connectors": [
              {
                "type": "IEC_62196",
                "phases_count": 3,
                "current_a": 32.0,
                "power_kw": 22.0
              }
            ]
          }
        ]
      }
    ]
  }
}
```

## SUB `sessions_history_response`

| Name           | Type                      | Description                                                    | Notes                                            |
|----------------|---------------------------|----------------------------------------------------------------|--------------------------------------------------|
| uuid           | `UUIDv4`                  | ID сессия зарядки                                              | `4b69e2d6-139a-463a-9c6b-5ff8e3bf38c3`           |
| space          | `object`                  | Парковочное место (станция)                                    | -                                                |
| space.id       | `int`                     | ID места                                                       | 1                                                |
| space.name     | `string`                  | description                                                    | 003                                              |
| lot            | `object`                  | Парковка                                                       | -                                                |
| lot.id         | `int`                     | ID парковки                                                    | 1                                                |
| lot.name       | `string`                  | Название парковки                                              | Конгрессная 31к1                                 |
| lot.city       | `string`                  | Город                                                          | Краснодар                                        |
| connector_type | `string`                  | тип коннектора для картинки и надписи                          | IEC_62196                                        |
| created_at     | `int`                     | дата когда началась сессия                                     | 1682053389                                       |
| finished_at    | `null\|int`               | дата когда закончилась сессия. format                          | 1682053881                                       |
| cost_total     | `str`                     | в рублях, буквально сумма (cost_kw + cost_idle + cost_booking) | 1020.00                                          |
| cost_kw        | `str`                     | в рублях, потрачено денег на электроэнергию                    | 870.80                                           |
| cost_idle      | `str`                     | в рублях, потрачено денег за простой на парковке               | 50.00                                            |
| cost_booking   | `str`                     | в рублях, сколько стоило бронирование                          | 100.00                                           |
| kw             | `float`                   | сумма накрученных киловатт                                     | 51.3                                             |
| idle_duration  | `int`                     | Время простоя                                                  | 13500 = "3ч 45мин"                               |
| duration       | `int`                     | в секундах                                                     | 13500 = "3ч 45мин"                               |
| status         | `"FIN" \| "NOM" \| "ACT"` | Статус этой сессии зарядки                                     | FIN - завершено, NOM - без оплаты, ACT - активно |

> Пример сообщения

```json
{
  "type": "sessions_history_response",
  "data": [
    {
      "uuid": "4b69e2d6-139a-463a-9c6b-5ff8e3bf38c3",
      "space": {
        "id": 3,
        "name": "003"
      },
      "lot": {
        "id": 1,
        "name": "Конгрессная 31к1",
        "city": "Краснодар"
      },
      "connector_type": "J1772",
      "created_at": 1687012408,
      "finished_at": 1687022798,
      "cost_total": 0.0,
      "cost_kw": 0.0,
      "cost_idle": 0,
      "cost_booking": 0,
      "kw": 10.91,
      "duration": 10389,
      "status": "FIN"
    },
    {
      "uuid": "ebcd520a-bc7d-42b8-a8c2-303872b962b3",
      "space": {
        "id": 3,
        "name": "003"
      },
      "lot": {
        "id": 1,
        "name": "Конгрессная 31к1",
        "city": "Краснодар"
      },
      "connector_type": "J1772",
      "created_at": 1686851298,
      "finished_at": 1686869301,
      "cost_total": 0.0,
      "cost_kw": 0.0,
      "cost_idle": 0,
      "cost_booking": 0,
      "kw": 17.136,
      "duration": 18002,
      "status": "NOM"
    }
  ]
}
```

## SUB `session_chart_response`

В формате популярных библиотек отрисовки Line графиков,
например [chart.js](https://www.chartjs.org/docs/latest/charts/line.html).

| Name       | Type           | Description                                                                  | Notes |
|------------|----------------|------------------------------------------------------------------------------|-------|
| order_uuid | UUIDv4         | ID сессии зарядки                                                            | -     |
| labels     | `list[number]` | список меток по оси x. В нашем случае это метки времени. seconds since Epoch | -     |
| current_a  | `list[number]` | массив меток по оси y для мгновенных ампер                                   | -     |

> Пример сообщения

```json
{
  "type": "session_chart_response",
  "data": {
    "order_uuid": "84f802b7-0dcb-49e3-9c3e-927dbb35e73d",
    "labels": [
      1684922095,
      1684922096,
      1684922097,
      1684922098
    ],
    "current_a": [
      13,
      13,
      10,
      7
    ]
  }
}
```

## SUB `book_space_response`

Если нет бронирования у пользователя, то придет сообщение с пустым `data`.

| Name           | Type     | Description                | Notes                            |
|----------------|----------|----------------------------|----------------------------------|
| booking_id     | `string` | ID бронирования            | в формате UUIDv4                 |
| space_id       | `string` | ID станции зарядки         | которую забронировали            |
| connector_type | `string` | Тип коннектора             | который выбрали при бронировании |
| created_at     | `number` | Дата создания бронирования | миллисекунды с начала эпохи      |
| until          | `number` | До какой даты бронирование | миллисекунды с начала эпохи      |
| cost           | `str`    | Стоимость бронирования     | в рублях                         |

> Пример сообщения

```json
{
  "type": "book_space_response",
  "data": {
    "booking_id": "b2cf9d52-da09-43d8-97de-348ffe12784f",
    "space_id": 5,
    "connector_type": "TES_US",
    "created_at": 1689054254000,
    "until": 1689057854000
  }
}
```

> Пример сообщения, если нет бронирования

```json
{
  "type": "book_space_response",
  "data": null
}
```

## SUB `cancel_bookings_response`

> Пример сообщения

```json
{
  "type": "cancel_bookings_response"
}
```

## SUB `payment_url_response`

> Пример сообщения

```json
{
  "type": "payment_url_response",
  "data": {
    "url": "https://alfa-charge-eco-nrg.server.paykeeper.ru/bill/20230822143604958"
  }
}
```

## SUB `get_payments_response`

| Name       | Type     | Description                | Notes                           |
|------------|----------|----------------------------|---------------------------------|
| uuid       | `string` | UUID платежа               | в формате UUIDv4                |
| cost_total | `string` | Сумма пополнения в рублях  | число с 2 знаками после запятой |
| created_at | `number` | Дата создания бронирования | миллисекунды с начала эпохи     |
| status     | `string` | Статус платежа             |                                 |

### Статусы платежа

| Name     | Description            | Notes                                                   |
|----------|------------------------|---------------------------------------------------------|
| PENDING  | Платеж инициализирован | Платеж инициализирован, но еще не оплачен пользователем |
| PAID     | Платеж оплачен         | Платеж принят, деньги списаны с лицевого счета          |
| CANCELED | Платеж отменен         | Платеж отменен, как правило если прошло много времени   |
| REFUNDED | Платеж возращен        | Сделан возврат денежных средств пользователя            |

### Cтатусы обработки платежа

| Name            | Description                        | Notes                                                                                                                                 |
|-----------------|------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------|
| CREATED         | Платеж создан                      | Означает, что наш API получил запрос пользователя и сейчас начнет работать с банком                                                   |
| PENDING_LINK    | Ожидание ссылки для оплаты         | Ожидаем, когда банк создаст ссылку для платежа                                                                                        |
| PENDING_WEBHOOK | Ожидание ответа от банка           | Как только пользователь заплатит или отменит или просто не заплатит, сервер отправит нам уведомление. До этого будет статус ожидания. |
| SUCCESS         | Успех                              | Платеж принят, деньги начислены на лицевой счет пользователя.                                                                         |
| CANCELLED       | Платеж отменен пользователем       | На платежной форме пользователь мог отменить оплату.                                                                                  |
| FAILED_LINK     | Ошибка получения ссылки для оплаты |                                                                                                                                       |
| FAILED_WEBHOOK  | Ошибка ответа от банка             |                                                                                                                                       |
| FAILED          | Ошибка                             | Что-то еще пошло не так в процессе.                                                                                                   |

> Пример сообщения

```json
{
  "type": "get_payments_response",
  "data": [
    {
      "uuid": "4b69e2d6-139a-463a-9c6b-5ff8e3bf38c4",
      "cost_total": 100.0,
      "created_at": 1689054254000,
      "status": "PAID"
    }
  ]
}
```

## SUB `convert_bonuses_response`

> Пример сообщения

```json
{
  "type": "convert_bonuses_response",
  "data": {
    "msg": "Бонусы успешно конвертированы в рубли",
    "status": "success",
    "balance": 530.0,
    "bonus_balance": 900.0
  }
}
```

## SUB `error_response`

Если отправленное сообщение вызвало ошибку, то сервер отправит это сообщение с деталями ошибки.

| Name     | Type       | Description                           | Notes                          |
|----------|------------|---------------------------------------|--------------------------------|
| message  | `string`   | Текст ошибки                          | -                              |
| errors?  | `object[]` | Массив ошибок                         | Это ошибки валидации сообщений |
| request? | `string`   | Тип сообщения, которое вызвало ошибку | Пример: `start_session`        |
| code     | `number`   | Код ошибки (не используется)          | -                              |

> Пример сообщения

```json
{
  "type": "error_response",
  "data": {
    "message": "Невозможно войти с предоставленным токеном",
    "code": 400
  }
}
```

TODO: добавить пример, где есть `errors`.

| Name | Type | Description | Notes |
|------|------|-------------|-------|
| name | type | description | notes |

> Пример сообщения

```json
{}
```

## SUB `payment_response`

Получение информации по конкретному платежу.
Например, в случае подтверждение платежа по вебхукe

| Name       | Type     | Description            | Notes            |
|------------|----------|------------------------|------------------|
| uuid       | `string` | UUID платежа           | в формате UUIDv4 |
| pay_amount | `float`  | Сумма платежа в рублях |                  |
| status     | `string` | Статус платежа         |                  |

> Пример сообщения

```json
{
  "type": "payment_response",
  "data": {
    "uuid": "9d8a1187-f20a-4d62-9add-2b62c7e7255f",
    "pay_amount": 10.0,
    "status": "PAID"
  }
}
```
