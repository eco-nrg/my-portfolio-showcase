# Station

Набор сервисов для работы станции зарядки на Raspberry PI.

## Запуск системы

Для деплоя используется systemd.

Предполагается, что вы склонировали код в папку `/home/raspi/python/station`.

## Настройка операционной системы

```shell
sudo apt update
sudo apt upgrade
sudo apt install git python3 tmux htop redis
```

### Настройка hostname

`sudo nano /etc/hostname`

И написать там одной строкой `rasp400N`, где N - это номер станции.

`sudo nano /etc/hosts`

Добавить строку `127.0.1.1    rasp400N`.

Изменения вступят в силу после перезапуска. Чтобы изменить имя хоста прямо сейчас: `sudo hostname rasp400N`.

### Установка python

1. Сначала установите python3 на система.
2. Установка паркетов:

```shell
cd /home/raspi/python/station
python3 -m venv venv
source venv/bin/activate
pip install -U pip setuptools
pip install -r requirements.txt
```

3. Задать PYTHONPATH на корень проекта:

```shell
nano venv/lib/python3.9/site-packages/env_vars.pth
вставить /home/raspi/python/station/ в файл env_vars.pth
```

### Настройка светодиодов на станции

Для работы свотодиодов на станции использутся библиотека pigpio. Для ее настройки используйте

```shell
sudo systemctl enable pigpiod.service
sudo systemctl start pigpiod.service
```

### Установка [pyqt](https://pypi.org/project/PyQt5/) c [qml](https://doc.qt.io/)

```shell
sudo apt-get install -y --no-install-recommends python3 python3-pip python3-pyqt5 python3-pyqt5.qtquick python3-pyqt5.qtsvg python-is-python3  qml-module-qtquick2  qml-module-qtquick-controls2 qml-module-qtquick-layouts  qml-module-qtquick-templates2  qml-module-qtquick-window2  qml-module-qt-labs-qmlmodels
```

### Запуск сервисов

1. Создайте файл `.env` по шаблону:  `cp /home/raspi/python/station/.template.env /home/raspi/python/station/.env` и установите нужные параметры в `.env` файле.
2. Скопируйте файлы из папки `/home/raspi/python/station/systemd` в `/etc/systemd/system`.
3. Загрузити конфиги systemd `sudo systemctl daemon-reload`.
4. Проверьте что, systemd обнаружил сервисы: `systemctl list-unit-files app*`.
5. Добавьте сервисы в автозагрузку: `sudo systemctl enable app-autofinish.service app-extra-stats.service app-camera.service app-light.service app-meter.service app-parklock.service app-ultrasonic.service app-ui.service app-config.service app-light-station.service app.service`.
6. Запустите все сервисы `sudo systemctl start app`. Чтобы перезагрузить сервисы: `sudo systemctl restart app`. Чтобы остановить все сервисы `sudo systemctl stop app`.
7. Смотреть логи командой `journalctl -f -u app-(SERVICE_NAME)`.

### Запуск сервисов из терминала

Для запуска сервисов из терминала необходимо перенести данные из  `.env` файл в `/home/raspi/.profile`

```shell
nano /home/raspi/.profile
export API_URL=https://api.eco-nrg.store
export APP_URL=https://charge.eco-nrg.store
export API_TOKEN=???
export TOKEN_KEY=???
export DEVICE_KEY=
export SENTRY_DSN=???
export SENTRY_ENV=???
```

## Настройка сбора метрик

Каждая станция отправляет метрики на сервер InfluxDB с помощью агента [telegraf](https://docs.influxdata.com/telegraf/).

### Установка Telegraf

Инструкция по установке: https://docs.influxdata.com/telegraf/v1.26/install/

```shell
wget -q https://repos.influxdata.com/influxdata-archive_compat.key
echo '393e8779c89ac8d958f81f942f9ad7fb82a25e133faddaf92e15b16e6ac9ce4c influxdata-archive_compat.key' | sha256sum -c && cat influxdata-archive_compat.key | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/influxdata-archive_compat.gpg > /dev/null
echo 'deb [signed-by=/etc/apt/trusted.gpg.d/influxdata-archive_compat.gpg] https://repos.influxdata.com/debian stable main' | sudo tee /etc/apt/sources.list.d/influxdata.list
sudo apt-get update && sudo apt-get install telegraf
```

Положить конфиг:

```shell
cp /home/raspi/python/station/telegraf.conf /etc/telegraf/telegraf.conf
```

Перезапустить или остановить сервис через systemd. Конфиг лежит в `/lib/systemd/system/telegraf.service`.

```sh
sudo systemctl restart telegraf
```
