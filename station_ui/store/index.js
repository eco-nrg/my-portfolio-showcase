export const state = () => ({
  getFormat: {// Экраны на станции и их команды
    baseImg: ['logo', 'qr-code', 'warning', 'charging_start'], // Базовое отображение картинок
    slideImg: ['charging_down', 'charging_end'], // Анимация со сменой слайдов
    customImg: ['charging']// Анимация в зависимости от станции где запущен сервер
  },
  response: '', // статус сервера
  timerSlideChange: 1000,// Время показа слайда
  chargingStation: 1, // штекер: 1-tesla_us, 2-iec_62196, 3-j1772
  created_at: Date.now(),// дата окончания зарядки в секундах
  start_payed: null,
  freeTime: 18000,
  am: 0,// колличество ампер
  current_kwh: 0,// колличество ват
  total_kwh: 0,// колличество киловат
  sliderCounts: 1 // сколько картинок в слайдаре
})

export const mutations = {
  setState(state, value) {// Обновляем данные пришедшие с сервера
    for (const key in value) {
      if (Object.hasOwnProperty.call(value, key)) {
        state[key] = parseFloat(value[key]) ? parseFloat(value[key]) : value[key];
      }
    }
  }
}

export const actions = {
  async request({ commit }) {// Запрос данных
    let data = []
    if (this.$axios){
      data = await this.$axios.$get(this.$axios.defaults.baseURL)
        .catch(function (error) {
          return { response: "warning" }// Если сервер не отвечает возвращаем кран ошибки
        })
    }
    if (process.env.NODE_ENV === 'deve')
      console.log("request", data );

    await commit('setState', data)
  }
}

export const getters = {}
