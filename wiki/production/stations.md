# Управление устройством на станции

На станции все управляется с помощью Raspberry Pi, которые подключены к интернету через GSM модем. У станций нет выделенного публичного ip адреса, поэтому они находятся в специальной виртуальной сети 10.8.x.x.

Варианты подключения:

- ssh
- vnc (для отладки дисплея)

## SSH доступ

Чтобы не настраивать локально vpn, можно зайти на станцию через двойной ssh:

```bash
ssh -A eco-parking-vpn
# мы на сервере vpn
ssh -A raspi@10.8.x.x # это ip адрес raspberry pi
```

`eco-parking-vpn` - это [[vpn]] сервер.
`raspi@10.8.X.X` - это ip адрес станции, ищи адреса тут [[Продакшен]]

Флаг `-A` для проброса ssh ключа дальше.

```
# ~/.ssh/config
Host eco-parking-vpn
    HostName 193.42.113.39
    User econrg
    Port 22

Host eco-pi_1
    HostName 10.8.0.54
    User raspi
    ProxyJump eco-parking-vpn

Host eco-pi_2
    HostName 10.8.0.62
    User raspi
    ProxyJump eco-parking-vpn

Host eco-pi_3
    HostName 10.8.0.66
    User raspi
    ProxyJump eco-parking-vpn

Host eco-pi_4
    HostName 10.8.0.70
    User raspi
    ProxyJump eco-parking-vpn
```

## VNC доступ

На своем компьютере надо поставить vnc viewer.

В консоли локального компьютера надо пробросить порт нужной станции: `ssh -L 5900:localhost:5900 -N eco-pi_X`

## Устройства

## 001

- город: Краснодар
- адрес: Конгрессная 31к1
- позиция: в центре
- device: `001 Raspberry 4 2GB`
  - ip [[vpn]]: `10.8.0.54`
  - ip local: `10.0.0.182`
- disk: `001 ssd 60GB`
- счетчик: [[74 Меркурий 234 ART-01 POR]]
- парклок mac address `CE-A4-CF-75-61-50`
- wall connector: [[Tesla EU - 3ф]]
- user: `raspi`
- pwd: `a123456b`

## 002 

- город: Краснодар
- адрес: Конгрессная 31к1
- позиция: слева
- device: `002 Raspberry 4 8GB`
  - ip [[vpn]]: `10.8.0.62`
  - ip local: `10.0.0.157`
- disk: `002 ssd 60GB`
- счетчик: [[65 Меркурий 234 ARTM2-02 POBR.R]]
- парклок mac address `E2-4C-2E-15-10-71`
- wall connector: [[Tesla US - 1ф]]
- user: `raspi`
- pwd: `a123456b`

## 003

- город: Краснодар
- адрес: Конгрессная 31к1
- позиция: справа
- device: `003 Raspberry 4 4GB`
  - ip [[vpn]]: `10.8.0.66`
  - ip local: `10.0.0.175`
- disk: `002 ssd 60GB`
- счетчик: [[95 Меркурий 234 ART-01 POR]]
- парклок mac address `CB-D0-00-CD-2E-49`
- wall connector: [[Jesla jp-us 1ф]]
- user: `raspi`
- pwd: `a123456b`

## 004

- город: Краснодар
- адрес: Уральская 138
- позиция: ?
- device: `004 Raspberry 4 4GB`
  - ip [[vpn]]: `10.8.0.70`
  - ip local: `10.0.0.218`
- disk: `/dev/sda2 ssd 60GB`
- счетчик: [[26 Меркурий 234 ART-01 POR]]
- парклок mac address `????`
- wall connector: [[IEC 62196]]
- user: `raspi`
- pwd: `a123456b`
- TOKEN_KEY: `cfe7fedb75b69bd5bf42d1fb69d91c783d61c27a`