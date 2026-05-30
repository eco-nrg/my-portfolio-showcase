# Продакшен

## Лэндинг страница

url: [eco-nrg.store](https://eco-nrg.store/)
host: хостинг [[reg-ru]]
dns-provider: [[reg-ru]]

## Головной сервер

Запущен на [[Selectel]].
API и статика задеплоена в docker-compose в `/opt/eco-nrg`. Для хостинга статики используется caddy внутри докера, НЕ nginx.
[Репозиторий с конфигурацией](https://gitlab.7bits.it/eco-parking/deployment)

- API: [api.eco-nrg.store](https://api.eco-nrg.store) - на странице будет 404 ошибка. Так и должно быть
- Web APP: [charge.eco-nrg.store](https://charge.eco-nrg.store) - приложение для активации станции с мобильного телефона
- ssl: letsencrypt
- ip: `84.38.181.131`
- user: `root`
- dns-provider: [[reg-ru]]
