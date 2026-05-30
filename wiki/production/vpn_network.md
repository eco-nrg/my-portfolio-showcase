# VPN

Вся система объединена в одну сеть с помощью openVPN.

Сервера собирались по следующим инструкциям:

- https://www.digitalocean.com/community/tutorials/how-to-set-up-and-configure-a-certificate-authority-ca-on-ubuntu-20-04-ru
- https://www.digitalocean.com/community/tutorials/how-to-set-up-and-configure-an-openvpn-server-on-ubuntu-20-04-ru
- https://www.youtube.com/watch?v=mVwT4FzvvKc

## VPN сервер

Запущен на [[RuVDS]]

`ssh root@193.42.113.39`
`ssh econrg@193.42.113.39`

ip: `193.42.113.39`

user: `root`
pwd: `itisnotthatdifficulttoremember`

sudo-user: `econrg`
pass: `doyouhaveteslabitch`

vpn-ip: `10.8.0.1`

### vpn profile

Пароль (pass phrase) ЦС: `NikolaElonTeslaMusk77777`
Common name: `EcoNrgVpnCA`

### docs

Важно
В vpn-конфиг добавлен ключ tls-auth (ta.key в /etc/openvpn/server). Иметь в виду, что микротик не поддерживает эту методику, поэтому, если появится оборудование от микротик, этот метод нужно обязательно удалить.

Шаги для создания нового ovpn
Сперва запускаем виртуалку ЦС.

Логин: lev

Пароль: 852456



Подключаем её к vpn-серверу:

cd my-key

openvpn3 session-start --config ca-serv.ovpn



Подключаемся сторонней машиной к vpn-серверу: 

ssh econrg@193.42.113.39

Или, если машина подключена по vpn к серверу:

ssh econrg@10.8.0.1

Далее следуем пунктам:

На vpn-сервере запустить скрипт ~/easy-rsa/sen-req.sh имя-подключения
На сервере ЦА запустить скрипт ~/easy-rsa/sign-new-req.sh имя-подключения
На vpn-сервере запустить скрипт ~/client-configs/make_config.sh имя-подключения
Забрать файл ovpn из ~/client-configs/files
Добавить в файл ovpn строчку auth-user-pass, чтобы при подключении запрашивался пароль
Идём в /etc/openvpn/server/scripts
Открываем auth-script.sh.passwd, прописываем пару имя-подключения:пароль, сохраняем
Пример. Допустим, надо создать ключ для малины. Придумываем название типа raspberry-dev-1

Запускаем скрипт:

./sen-req.sh raspberry-dev-1

Следуем инструкциям скрипта: 

спросит про Common Name - жмём enter, т.к. Common Name у нас вписан, это raspberry-dev-1, 
вводим пароль юзера ЦС для передачи на ЦС запроса с помощью scp


Далее на ЦС:

./sign-new-req.sh raspberry-dev-1

Следуем инструкциям скрипта: 

вводим “yes”, 
вводим pass phrase ЦС: NikolaElonTeslaMusk77777,
вводим пароль юзера econrg для передачи инфы на vpn-сервер с помощью scp
На vpn-сервере запускаем

/make_config.sh raspberry-dev-1, файл ovpn готов. Осталось добавить в него auth-user-pass для подключения по паролю. Мне было лень заниматься автоматизацией включения этой записи в конфиг, поэтому при желании можешь изучить, как сделать так, чтобы эта запись добавлялась автоматически.

В /etc/openvpn/server/scripts/auth-script.sh.passwd прописываем что-то вроде ras:123456 

Поздравляю, ты молод, успешен, и можешь подключить ещё одну машину к серверу.

Если надо добавить пользователя без пароля
Я написал простейший bash-скрипт для проверки пароля. Он лежит по этому адресу:

/etc/openvpn/server/scripts/auth-script.sh

На момент написания инструкции 20.07.22 в список подключений без пароля входят:

gelendzhik-station-001, 
ca-serv,
client1 (можно удалить, это ключ Льва)
Модифицируйте как хотите.

Прочее
Адрес лога:

/var/log/openvpn/openvpn-status.log, там видны текущие подключения в том числе

Адрес конфига и логин-файла

/etc/openvpn/server/scripts



Полезный копипаст

sudo systemctl restart openvpn-server@server.service



auth-user-pass