# Компоненты системы EcoParking

Документ описывает устройство автоматизированной станции зарядки электромобилей.

## Введение

Сервис зарядки состоит из программно-аппаратного комплекса станции зарядки на уличной парковке, мобильного приложения для активации зарядки пользователем, головного сервера.

## Программные сервисы

- [eco-nrg.store](http://eco-nrg.store/) — лендинг, рекламная страница сервиса
- [charge.eco-nrg.store](http://charge.eco-nrg.store/) — мобильное приложение для активации станции, просмотра [[IP_Cameras|камер наблюдения]], пополнения счета
- [api.eco-nrg.store](http://api.eco-nrg.store/) — API для мобильного приложения и станций зарядок. Конечные пользователи не заходят на этот сайт.
- [api.eco-nrg.store/my_admin/](http://api.eco-nrg.store/my_admin/) — Админка системы для настройки станций, просмотра заказов, пользователей, и т.д. Используется только админами
- [stats.eco-nrg.store/](https://stats.eco-nrg.store/) — Интерфейс для просмотр статистики станций на [[Графана]]. Используется только админами
- [[RaspberryPi]] управляют камерами наблюдения, дисплеем станции, парклоками, снимают показания со счетчика, и т.д. Прямого доступа к ним нет, только через внутреннюю подсеть [[vpn]].

## Программно-аппаратный комплекс станции зарядки

1. Микрокомпьютер [[RaspberryPi]].
2. [[Счетчики|Счетчик]] электроэнергии, подключенный к электросети.
3. Коннектор зарядки.
4. Датчик вставленного на место коннектора (пистолета) зарядки.
5. [[Parklock]] наземный шлагбаум
6. [[IP_Cameras|IP-Камеры наблюдения]].
7. Дисплей.
8. Светодиод статуса станции.
9. GSM-модем и маршрутизатор.
10. Видео-регистратор.
11. Ультразвуковой датчик расстояния.
12. Лидар — точный датчик расстояния. (Будет вместо Ультразвукового)

{{plantuml
@startuml station

cloud Internet

boundary Electricity

component Mercuriy
component Parklock
component Gerkon
component Display
component Ultrasonic
component Led_RGB
component Led_Parklock
component Led_Ultrasonic

node RaspberryPi {
  port Pow
  port USB
  portout Pin1
  portout Pin2
  portout Pin3
  portout Pin4
  portout Pin5
  portout Pin6
  portout Pin7
  port ETH
  port BT
  port HDMI
}

component IpCamera
component Router

actor Car

Pin1 .. Gerkon
Pin2 .. Ultrasonic
Pin3 .. Led_RGB: Red
Pin4 .. Led_RGB: Green
Pin5 .. Led_RGB: Blue
Pin6 .. Led_Ultrasonic
Pin7 .. Led_Parklock

Mercuriy .. USB
Parklock ~~ BT
Router .. ETH
Display .. HDMI

Router .. IpCamera : ETH
Router ~~ Internet : GSM

Electricity -- Mercuriy


Mercuriy -- Car : Connector

@enduml

}}
