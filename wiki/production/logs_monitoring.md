# Логи и мониторинг

## Сырые логи сервера

[tail.eco-nrg.store](https://tail.eco-nrg.store/)

Используется сервис [dozzle](https://github.com/amir20/dozzle) для показа логов docker контейнеров.

user: `logger`
password: `bepolite`

## Glitchtip - мониторинг ошибок 

Система для уведомления об ошибках. Задеплоено на отдельном сервере.

Причины выбора [Glitchtip](https://glitchtip.com/).
Glitchtip это как Sentry, только попроще и менее требовательна к железу. Sentry нынче использует кафку и snuba, которые требуют около 4гб оперативы и 4 cpu. 

[logs.eco-nrg.store](https://logs.eco-nrg.store/)

user: `ilya.siganov@7bits.it`
pwd: `qweqweasdLogs`

### Информация о сервере Glitchtip

provider: [[Selectel]]
dns-provider: [[Reg-ru]]

domain: `logs.eco-nrg.store`
host: `45.131.41.230`
user: `root`
auth: ssh keys

