# ECO-PARKING

Зарядные станции электромобилей. [Кодовая база в Gitlab](https://gitlab.7bits.it/eco-parking).

## Продакшен

- [eco-nrg.store](http://eco-nrg.store/) — лендинг, рекламная страница сервиса
- [charge.eco-nrg.store](http://charge.eco-nrg.store/) — мобильное веб приложение для пользователей
- [api.eco-nrg.store](http://api.eco-nrg.store/) — API для мобильного приложения и станций зарядок. Конечные пользователи не заходят на этот сайт.
- [api.eco-nrg.store/my_admin/](http://api.eco-nrg.store/my_admin/) — Админка системы для настройки станций, просмотра заказов, пользователей, и т.д. Используется только админами
- [stats.eco-nrg.store/](https://stats.eco-nrg.store/) — Интерфейс для просмотр статистики станций на [[Графана]]. Используется только админами
- [tail.eco-nrg.store](https://tail.eco-nrg.store/) — Сырые логи докер контейнеров API сервера
- [logs.eco-nrg.store](https://logs.eco-nrg.store/) — Мониторинг ошибок glitchtip/sentry
- [api.eco-nrg.store/static/live/](https://api.eco-nrg.store/static/live/) — Все камеры в одном месте
- [api.eco-nrg.store/report](https://api.eco-nrg.store/report) — Отчеты по использованию зарядками

## Тестовые сервера

- [eco-parking.7bits.it](http://eco-parking.7bits.it/) — мобильное веб приложение для пользователей
- [api.eco-parking.7bits.it/my_admin/](http://api.eco-parking.7bits.it/my_admin/) — Админка
- [pi.eco-parking.7bits.it](https://pi.eco-parking.7bits.it/) — эмулятор станции зарядки
- [tail.eco-parking.7bits.it](https://tail.eco-nrg.store/) — Сырые логи докер контейнеров API сервера
- [logs.eco-parking.7bits.it](https://logs.eco-nrg.store/) — Мониторинг ошибок glitchtip/sentry