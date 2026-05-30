# IP Cameras

https://api.eco-nrg.store/static/live/

- 001 `rtsp://10.0.0.14:554/user=admin&password=&channel=1&stream=0.sdp/`
- 002 `rtsp://10.0.0.10:554/user=admin&password=&channel=1&stream=0.sdp/`
- 002 `rtsp://10.0.0.146:554/user=admin&password=&channel=1&stream=0.sdp/`
- 003 `rtsp://10.0.0.160:554/user=admin&password=&channel=1&stream=0.sdp/`
- 004 `rtsp://192.168.88.231:554/user=admin&password=&channel=1&stream=0.sdp/` (пароль в web интерфейса `admin:qwe123ASD`)
- 004 `rtsp://192.168.88.209:554/user=admin&password=a123456b&channel=1&stream=0.sdp/` (пароль в web интерфейса `admin:a123456b`)

Для настройки камер (например времени) можно использовать эту утилиту:  `pip install python-dvr` ([sources](https://github.com/NeiroNx/python-dvr))

Для настройки времени на камерах нужно физически настроить местный видео регистратор (уточнить как).
