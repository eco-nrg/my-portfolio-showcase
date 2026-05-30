DOCKER_STAGING = docker compose -f docker-compose.yaml -f compose.staging.yaml
DOCKER_PROD = docker compose -f docker-compose.yaml

.PHONY: all
all: build_staging

.PHONY: redeploy_staging
redeploy_staging:
	$(DOCKER_STAGING) build
	$(DOCKER_STAGING) down
	$(DOCKER_STAGING) up -d

.PHONY: redeploy_staging_api
redeploy_staging_api:
	$(DOCKER_STAGING) build api cron
	$(DOCKER_STAGING) stop api cron
	$(DOCKER_STAGING) rm api cron -f
	$(DOCKER_STAGING) up api cron -d

.PHONY: redeploy_staging_web
redeploy_staging_web:
	$(DOCKER_STAGING) build webapp
	$(DOCKER_STAGING) stop webapp
	$(DOCKER_STAGING) rm webapp -f
	$(DOCKER_STAGING) up webapp -d

.PHONY: build_prod
build_prod:
	$(DOCKER_PROD) build

.PHONY: redeploy_prod
redeploy_prod: build_prod
	$(DOCKER_PROD) down
	$(DOCKER_PROD) up -d

.PHONY: redeploy_prod_webapp
redeploy_prod_webapp:
	$(DOCKER_PROD) build webapp
	$(DOCKER_PROD) stop webapp
	$(DOCKER_PROD) rm webapp -f
	$(DOCKER_PROD) up webapp -d

.PHONY: redeploy_prod_api
redeploy_prod_api:
	$(DOCKER_PROD) build api cron
	$(DOCKER_PROD) stop api cron
	$(DOCKER_PROD) rm api cron -f
	$(DOCKER_PROD) up api cron -d