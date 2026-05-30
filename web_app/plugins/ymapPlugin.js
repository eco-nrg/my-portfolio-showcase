import Vue from 'vue'
import YmapPlugin from 'vue-yandex-maps'


const settings = {// настройки подключения к карте yandex
	apiKey: process.env.API_MAP_KEY || '',/// Купить ключь
  lang: 'ru_RU',
  coordorder: 'latlong',
  enterprise: false,
  debug: true,
  version: '2.1',
  debug: true
}

Vue.use(YmapPlugin, settings);