# DB dumps

Все дампы лежать в [Гугл диске](https://drive.google.com/drive/folders/1PZhjsrXEWep-i9oe45kn6LPde7MfqGSm?usp=drive_link).

## Как делать дамп

```sh
docker exec -i deployment-db-1 /bin/bash -c  "PGPASSWORD=ПАРОЛЬ_В_ДОКЕР_КОМПОЗЕ pg_dump --username econrstore_prod econrstore_prod" > dump_ВСТАВЬ_ДАТУ.sql
```

- deployment-db-1 - это название контейнера. Оно может поменяться. Если что, смотри `docker ps`.
