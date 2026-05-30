# Тестирование

## Тестирование на стейджинге

### Тестовый стенд в 7bits

#### Здесь описаны данные для тестирования, которые нужны почти во всех кейсах/багах/фичах

**Открыть стейджинг**
http://eco-parking.7bits.it/

**Логин с заполненным профилем**
- открыть [админку](https://tracker.7bits.it/projects/eco-parking/wiki/Credentials#Django-admin)
- открыть [профили](https://api.eco-parking.7bits.it/my_admin/account/profile/)
- выбрать аккаунт с **заполненным** именем
- используем телефон из поля "User" на странице логина
- используем "Код входа" на следующей странице

**Логин без профиля** 
- открыть [админку](https://tracker.7bits.it/projects/eco-parking/wiki/Credentials#Django-admin)
- открыть [профили](https://api.eco-parking.7bits.it/my_admin/account/profile/)
- выбрать аккаунт с **пустым** именем
- используем телефон из поля "User" на странице логина
- используем "Код входа" на следующей странице

**Перейти на страицу зарядки Терминал 1**
https://eco-parking.7bits.it/spaces?id=1

**Перейти на страицу зарядки Терминал 2**
https://eco-parking.7bits.it/spaces?id=2

**Перейти на страицу зарядки Терминал 3**
https://eco-parking.7bits.it/spaces?id=3
