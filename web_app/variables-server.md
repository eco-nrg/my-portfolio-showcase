Базовые постоянные значения идут с любым ответом кроме неправильных запросов
{
	auth: string,// Нужен при авторизации в дальнейшем поле может не быть но появлятся при смене на сервере токена.
	cashData {
		money: float.// Сумма денег
		bonus: float,// Сумма бонусов
		freeTime: int,// число бесплатных секунд
	},
  book_state: 1 // id парковочного места null нет подписка СМС
        // 1 - Можно подписаться на обновления 
        # Планируется // 2 - Забронировано, но можно подписаться, когда освободится 
        // 3 - Пользователь уже подписан book_state === Refill.id
        // 4 - Текущий пользователь уже заряжается book_state === spaces/:id


	bonusUser: [// Доступные бонусы пользователя
    {
      command: 'new_user',// Командная строка Пока нет всего списка хз какие еще будут команды. На основе них идет обработка и пометка событий. Отдельным плагином
      summ: 100
    },
    {
      command: 'fill_profile',
      summ: 200
    }
  ],

  alertMessanger: [// Сообщения для пользователя красная стока
    {
      page: 'profile',
      command: 'fill_profile',
      icon: 'exclamation',
      messanger: 'Заполните профиль чтобы получать скидки и бонусы'
    }
  ]
}











Данные по точкам входа первоначальная загрузка получение по покетам.
варианты запроса:
	{// Вариант запроса авторизованного пользователя любая страница
		token: "68f3c458dd9d2c212bdf2c08cb2a3127d090d282",
		rout: "map",
		userAgent: "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.114 YaBrowser/22.9.1.1110 (beta) Yowser/2.5 Safari/537.36"
	}
	{// Вариант запроса авторизирующегося пользователя может что то поменятся и быть не профиль первой страницей
		phone: "79383093903",
		code: 654128,
		rout: "prifile",
		userAgent: "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.114 YaBrowser/22.9.1.1110 (beta) Yowser/2.5 Safari/537.36"
	}












1 Profile PAGE: {
	profileData: {//Данные профиля
		phone: string,
		first_name: string,
		middle_name string
	},
  filledProfile: false, //Заполнен профиль или нет
	carData: {//Данные машины
		model: string,
		manufacturer: string,
		number: string,
		year: int
	},
	batteryData: {//Данные батареи
		power: float,
		fast_type: float,
		slow_type: float
  },
  listModel: object, // список всех моделей маши нужны для поиска и заполнения профиля ключь это марка значение = массив опций
  listManufacturer: array // список всех марки маши нужны для поиска и заполнения профиля
}












1.1 edit Profile PAGE: {
  phone: string,
  first_name: string,
  middle_name string

  model: string,
  manufacturer: string,
  number: string,
  year: int

  power: float,
  fast_type: float,
  slow_type: float
}












2 Refill PAGE: [
  {
    name: string,
    station:
    [
      {
        img_map: string,
        img_cam: string,
        address: string,
        show: boolen, // выбрана заправка
        spaces:
        [
          {
            id: int,
            name: string,
            status: string,
            price_kwh: float,// sessionCharging
            price_parking: float,// sessionCharging
            connectors:
            [
              {
                type: string,
                phases_count: int,// sessionCharging
                current_a: float,// sessionCharging
                power_kw: float,// sessionCharging
              }
            ]
          },
        ]
      },
    ]
  },
]












3 Map PAGE { // https://yandex.ru/map-constructor/location-tool  / координаты и зум
  config: {
    coords: array, // [44.88271047121068, 38.285348554931616]
    zoom: int, // 9
    iconImageSize: array, // [30, 50], 
  },
  markers: [
    {
      index: int,
      name: string,
      address: string,
      coord: array, //[44.88271047121068, 38.285348554931616]
      spaces: [
        {
          id: int,
          status: string,
          connectors: [
            {
              connector_type: string,
              phases_count: int,
              power_kw: float,
              current_a: int
            },
          ]
        },
      ]
    },
  ]
}












4 Refill Select station PAGE: // пока не знаю данных нет
{
  img_map: string,
  img_cam: string,
  address: string,
  show: boolen, // выбрана заправка
  spaces:
  [
    {
      id: int,
      name: string,
      status: string,
      price_kwh: float,// sessionCharging
      price_parking: float,// sessionCharging
      connectors:
      [
        {
          type: string,
          phases_count: int,// sessionCharging
          current_a: float,// sessionCharging
          power_kw: float,// sessionCharging
        }
      ]
    },
  ]
}










5 History PAGE: // нет дизайна
[
  {
    activationTime: string,  // Дата и время активации
    sessionDuration: string, // Длительность сессии
    kWt: float,              // Использование эл. энергии
    type: string,            // Тип разьема
    id: int,                 // id станции
    status: string,          // Состояние станции сейчас
    cost: float,             // Стоимость
    details: {               // ссылкой в детализацию
      costParking: float,    // стоимость парковки
      rent: float,           // аренды оборудования
      compensation: float    // компенсация за использоаанную эл. энергию.
    }
  },
]












//Сессия зарядки
6 spaces/:id PAGE: {
  id: int,
  connector_type: string,
  created_at: string datatime,
  start_payed: null,           //Время начала платной зарядки
  cash: float,
  total_kwh: float,
  am: float,
  current_kwh: float,
  current_v: float,
  cam_1: string || '',
  cam_2: string || ''
}










