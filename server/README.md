# Eco Parking Space

## Eco Parking Backend

- [Eco Parking Space](#eco-parking-space)
  - [Eco Parking Backend](#eco-parking-backend)
  - [Technology stack](#technology-stack)
  - [Requirements](#requirements)
  - [Before start](#before-start)
  - [Start project](#start-project)
  - [API](#api)
  - [Tests](#tests)

## Technology stack

1. [Python](https://www.python.org/) 3.9.15
2. [Django](https://www.djangoproject.com/) 4.2.2
3. [Poetry](https://python-poetry.org/) 1.5.1
4. [PostgreSQL](https://www.postgresql.org/) 15.2
5. [Redis](https://redis.io/) 7.0
6. [Influxdb](https://www.influxdata.com/db/) 2.7

## Requirements

1. [Python](https://www.python.org/) (≥ 3.9.15)- for development. We recommend that you use [pyenv](https://github.com/pyenv/pyenv) for installation of python
2. [Poetry](https://python-poetry.org/) (≥ 1.5.1)
3. [Docker](http://docker.io) (≥ 18.09.7) - for development
4. [Docker Compose](https://docs.docker.com/compose) (≥ 1.17.1) - for development

## Before start

Before start you need have work PostgreSQL database and Django migration. (or start Docker with database and connect ports)
First of all you need start PostgreSQL database on port 5432. You can use docker-compose.yaml file for it or install PostgreSQL on your local machine.

```shell
docker compose build
docker compose up -d
```

Now, you can dump your database. You can find it in google disk.

```shell
docker exec -i server-db-1 psql -U econrstore_prod -d econrstore_prod < dump_name.sql
```

Next, you can apply Django migrations.

```shell
poetry shell
python manage.py migrate
```

## Start project

```shell
python manage.py runserver localhost:8080
```

## API

[apidoc.md](apidoc.md)

## Tests

```shell
poetry shell
poetry run pytest
```

## Create migrations

```shell
poetry shell
python manage.py makemigrations --name name_for_migration
```
