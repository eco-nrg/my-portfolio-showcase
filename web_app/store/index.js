const getDefaultState = () => ({
  phoneCheck: false,//Проверка номера телефона
  errorMsg: '',// Сообщения об ошибках
  isSessionCharging: false, // Активна ли сессия зарядки
  filledProfile: false,//Профиль заполнен?
  colorCash: null,//Цвет наличности в профиле
  colorCashMenu: null,//Цвет наличности в меню
  backgroundStatusColor: {
    AV: 'var(--green-light-fon)',
    DI: 'var(--black-text)',
    CH: 'var(--blue-fon-button)',
    BU: 'var(--conn-BU)',
    BO: 'var(--conn-BO)',
  },// Цвета фона статуса
  status: {
    AV: 'Свободно',
    DI: 'не Обслуживается',
    CH: 'Заряжает',
    BU: 'Занято',
    BO: 'Забронирована',
  },//Список статусов станции

  // Bases variables ///
  alertMessanger: [],//Сообщения для пользователю

  // profile data ///
  listModel: [],// Список моделей электроавтомобилей
  listModelAll: [],// Общий Список моделей электроавтомобилей
  listManufacturer: [], // Список марка электроавтомобилей
  fast_choices: [], // Список быстрой зарядки
  slow_choices: [],// Список медленной зарядки

  cashData: {},//Данные по деньгам
  profileData: {},//Данные профиля
  carData: {},//Данные машины
  batteryData: {},//Данные батареи

  bookSpace: {},// Бронирование

  // refill data ///
  listRefill: [],

  // map data ///
  map: {},//Карта yandex

  transactionData: false, //Пришли данные транзакций ?
  historyData: false,// Пришли данные сессий?
  history: [],// Страница истории
  transaction: [],// Страница транзакций
  chartHistory: {},

  // session data ///
  sessionCharging: {},

  sessionReceived: false,

  // Modal data
  nameModal: '', // Название окна
  typeModal: '', // Модель окна "бонус, ошибка, инфо (bonus, alert, info, chart)"
  dataModal: null, // Данные для модального окна

  isBooking: false,
  command: '',
});

export const state = () => getDefaultState();

export const mutations = {
  setAuthData(state, authData) {
    for (const key in authData) {
      if (Object.hasOwnProperty.call(authData, key)) {
        state[key] = authData[key];
      }
    }
  },
  setProfile(state, value) {
    for (const key in value) {
      if (Object.hasOwnProperty.call(value, key)) {
        if (key === "fast_choices" || key === "slow_choices") {
          state[key] = Object.values(value[key]).map(item => ({ value: item, selected: false }))
          state[key + 'All'] = value[key]
        } else {
          state[key] = value[key]
        }
      }
    }
  },
  setErrorResponse(state, value) {
    state.errorMsg = value;
  },
  setSessionCharging(state, value) {
    for (const key in value) {
      if (Object.hasOwnProperty.call(value, key)) {
        state.sessionCharging[key] = value[key];
      }
    }

    state.isSessionCharging = true
  },
  setSessionReceived(state) {
    state.sessionReceived = true;
  },
  isCharging(state, value = false) {
    if (value) {
      state.sessionCharging = {}
    }

    state.isSessionCharging = state.sessionCharging?.id > 0
  },
  setBookSpace(state, value) {
    state.bookSpace = value
  },
  setRefill(state, value) {
    if (state.listRefill.length) {
      for (let index = 0; index < state.listRefill.length; index++) {
        const element = state.listRefill[index];
        for (let idx = 0; idx < element.station.length; idx++) {
          const el = element.station[idx];
          if (el.show) {
            value[index].station[idx].show = true // оставляем открытую станцию
          }
        }
      }
    }
    state.listRefill = value
  },
  setMarkersAll(state, value) {
    state.map = value
  },
  setHistory(state, value) {
    for (const key in value) {
      value[key].show = false
    }

    state.history = value
    if (value.length > 0)
      state.historyData = false
    else
      state.historyData = true
  },
  setTransaction(state, value) {
    state.transaction = value
    if (value.length > 0)
      state.transactionData = false
    else
      state.transactionData = true
  },
  setChartHistory(state, value) {
    if (value.labels.length > 0) {
      state.chartHistory = value;
    } else if (state.nameModal === '') {
      state.nameModal = 'notChartData';
      state.typeModal = 'info';
    }
  },
  setProfileEdit(state) {
    state.nameModal = 'saveDateProfile';
    state.typeModal = 'bonus';
  },
  setBonusConvert(state, value) {
    state.nameModal = 'showBonusSuccess';
    state.typeModal = 'info';
    state.dataModal = value.msg;
  },
  setShowStation(state, value) {
    for (const key in state.listRefill) {
      if (Object.hasOwnProperty.call(state.listRefill, key)) {
        const element = state.listRefill[key];
        for (const k in element.station) {
          let item = element.station[k];

          if ((value.address === item?.address || item.spaces.filter(item => item.name === value.name).length) && !item.show) {
            item.show = true
          } else {
            item.show = false
          }
        }
      }
    }
  },
  setIsBooking(state, isBooking) {
    state.isBooking = isBooking;
  },
  showContext(state, value) {
    for (let i = 0; i < state.history.length; i++) {
      if (state.history[i].uuid === value.uuid) {
        state.history[i].show = !state.history[i].show
      }
    }
  },
  phoneCheck(state, value) {
    state.phoneCheck = value.code === 200 ? true : false
  },
  setPhoneCheck(state, value) {
    state.phoneCheck = value;
  },
  setColorCash(state, value) {
    state.colorCashMenu = (value == 0 ? 'var(--white-text)' : (value > 0 ? 'var(--green-dark-fon)' : 'var(--orange-rad)'))
    state.colorCash = (value == 0 ? 'var(--light-grey)' : (value > 0 ? 'var(--green-light-fon)' : 'var(--red-light-fon)'))
  },
  changeCamm(state, value) {
    state.sessionCharging.selected_camera = value
  },
  resetState(state) {
    Object.assign(state, getDefaultState())
  },
  serverResponseExpected(state, value) {
    state.nameModal = 'serverResponseExpected'
    state.typeModal = value
  },
  setModal(state, { name, type, data }) {
    state.nameModal = name;
    state.typeModal = type;
    state.dataModal = data;
  },
  setCommand(state, command) {
    state.command = command;
  },
};

export const actions = {
  setAuth(_, auth) {
    if (auth && auth !== '') {
      this.$cookies.set(
        'auth',
        auth,
        {
          maxAge: 60 * 60 * 24 * 7,
        },
      );
    } else {
      this.$cookies.remove('auth');
    }
  },
  async get_post_request({ commit, dispatch }, data) {
    let timeModalShow;
    if (data.url === 'payment_url' || data.url === 'convert_bonuses') {
      commit('serverResponseExpected', 'info');
      timeModalShow = setTimeout(commit, 5000, 'serverResponseExpected', 'alert');
    }

    const authToken = this.$cookies.get('auth');
    const headers = {};

    if (authToken && authToken !== '') {
      headers['Authorization'] = `Bearer ${authToken}`;
    }

    try {
      const response = await this.$axios.post(
        `${process.env.API_SERVER}/main/api/v1/${data.url}`,
        data.data,
        {
          headers,
        },
      );
      const resData = response.data

      if (data.url === 'payment_url' || data.url === 'convert_bonuses') {
        clearTimeout(timeModalShow);
        commit(
          'setModal',
          {
            name: '',
            type: '',
            data: null,
          },
        );
        if (resData?.url) {
          window.location.replace(resData.url);
        }
        return;
      }

      if (resData?.auth && resData.auth !== '') {
        await dispatch('saveAuthToken', resData);
        return;
      }

      if (resData?.code) {
        commit('phoneCheck', resData);
        return;
      }
    } catch (error) {
      if (error.response?.data?.detail) {
        commit('setErrorResponse', error.response.data.detail);
      } else {
        commit('serverResponseExpected', 'alert');
      }
      if (data.url === 'payment_url' || data.url === 'convert_bonuses') {
        clearTimeout(timeModalShow);
      }
    }
  },
  ///// EVENT SERVER START /////
  openWebsocket() {
      const token = this.$cookies.get('auth');
      if (!token) {
        return;
      }

      this.app.$socketManager.open(token);
  },
  onsubmit({ dispatch }, message) {
    if (this.app.$socketManager.isClosed()) {
      dispatch('openWebsocket');
    }
    this.app.$socketManager.send(message.type, message.data);
  },
  error_response({ commit }, data) {
    if (data?.message) {
      commit('setErrorResponse', data.message);
    }
  },
  clearErrorMsg({ commit }) {
    commit('setErrorResponse', '');
  },
  phone_auth_response({ commit }, data) {// Ответ сервера проверка токена авторизации
    commit('setAuthData', data);
  },
  profile_response({ commit }, data) {// Ответ сервера Данные пользователя
    commit('setProfile', data)
  },
  edit_profile_response({ commit }) {
    commit('setProfileEdit')
  },
  start_session_success({ commit }, data) {// Ответ сервера сессия зарядки началась успешно
    if (data?.id > 0) {
      commit('setSessionCharging', data);
    }
    this.$router.replace(`/spaces/${data.id}`);
    commit(
      'setModal',
      {
        name: '',
        type: '',
        data: null,
      },
    );
  },
  session_charging({ commit }, data) {// Ответ сервера Данные сессии зарядки
    if (data?.id > 0) {
      commit('setSessionCharging', data);
    }
    commit('setSessionReceived');
  },
  session_stop({ commit }) {// Ответ сервера, что зарядка завершена
    commit('isCharging', true);
    this.$router.replace('/profile');
  },
  refill_response({ commit }, data) {
    commit("setRefill", data)
  },
  map_response({ commit }, data) {
    commit("setMarkersAll", data)
  },
  sessions_history_response({ commit }, data) {
    commit('setHistory', data)
  },
  get_payments_response({ commit }, data) {
    commit('setTransaction', data)
  },
  session_chart_response({ commit }, data) {
    commit('setChartHistory', data)
  },
  book_space_response({ commit }, data) {
    commit('setBookSpace', data)
  },
  cancel_bookings_response({ commit }) {
    commit('setBookSpace', {})
  },
  message({ }, data) {//Сообщения от сервера если нет обработчика
    const dataReq = JSON.parse(data.data)
    console.log('%c store message Сообщения от сервера если нет обработчика', 'background: #222; color: #bada55', dataReq);
  },
  ///// EVENT SERVER END /////
  setIsBooking({ commit }, isBooking) {
    commit('setIsBooking', isBooking)
  },
  showContext({ commit }, data) {
    commit('showContext', data)
  },
  saveAuthToken({ dispatch }, data) {
    if (data?.auth) {
      dispatch('setAuth', data.auth);
      const queryParams = new URLSearchParams(window.location.search);
      const id = queryParams.get('id');
      if (id) {
        window.location.replace(`/spaces?id=${id}`);
      } else {
        window.location.replace('/profile');
      }
    }
  },
  __setColorCash({ commit }, data) {
    commit('setColorCash', data)
  },
  __setShowStation({ commit }, data) {
    commit('setShowStation', data)
  },
  __resetState({ commit, dispatch }) {
    dispatch('setAuth', null);
    commit('resetState');
    window.location.replace('/');
  },
  __setPhoneCheck({ commit }, data) {
    commit('setPhoneCheck', data);
  },
  modalCharge({ commit }, data) {
    commit('modalCharge', data);
  },
  setModal({ commit }, data) {
    commit('setModal', data);
  },
  closeModal({ state, commit }) {
    commit(
      'setModal',
      {
        name: '',
        type: '',
        data: null,
      },
    );
    if (state.command.length > 0) {
      commit('setCommand', '');
    }
  },
  setCommand({ commit }, command) {
    commit('setCommand', command);
  },
};

export const getters = {
  getKeyFastChoices(state) {
    return state.fast_choicesAll
  },
  getKeySlowChoices(state) {
    return state.slow_choicesAll
  },
  getDateRefill(state) {
    const arr = state.listRefill.map(i => ({
      name: i.name,
      station: i.station.map(e => ({
        address: e.address,
        spaces: e.spaces.map(s => ({
          id: s.id,
          name: s.name,
          status: s.status,
          position: s.position,
          connectors: s.connectors.map(c => ({
            type: c.type,
            power_kw: c.power_kw
          }))
        }))
      }))
    }))
    return arr
  },
};
