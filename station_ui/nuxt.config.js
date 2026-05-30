const isDev = process.env.NODE_ENV === 'deve'
export default {
  // Disable server-side rendering: https://go.nuxtjs.dev/ssr-mode
  ssr: false,

  // Global page headers: https://go.nuxtjs.dev/config-head
  head: {
    title: 'eco-energo-station',
    htmlAttrs: {
      lang: 'ru-RU',
      manifest: "default.appcache"
    },
    noscript: [{ innerHTML: "У вас отключен JavaScript. Сайт может отображаться некорректно. Рекомендуем включить JavaScript." }],
    meta: [
      { charset: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no' },
      { name: "HandheldFriendly", content: "True" },
      { "http-equiv": "Cache-Control", content: "no-cache" },
      { "http-equiv": "cleartype", content: "on" },
      { name: "apple-mobile-web-app-capable", content: "yes" },
      { name: "apple-mobile-web-app-status-bar-style", content: "black-translucent" },
      { "http-equiv": "X-UA-Compatible", content: "IE=edge" },
      { "http-equiv": "imagetoolbar", content: "no" },
      { "http-equiv": "msthemecompatible", content: "no" },
      { name: "format-detection", content: "telephone=no" },
      { name: "format-detection", content: "address=no" }
    ],
    link: [
      { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }
    ]
  },

  html: {
    minify: {
      collapseBooleanAttributes: true,
      decodeEntities: true,
      minifyCSS: true,
      minifyJS: true,
      processConditionalComments: true,
      removeEmptyAttributes: true,
      removeRedundantAttributes: true,
      trimCustomFragments: true,
      useShortDoctype: true
    }
  },

  loading: '~/components/loading.vue',

  // Global CSS: https://go.nuxtjs.dev/config-css
  css: [
    '~/assets/css/main.css',
  ],

  // Plugins to run before rendering page: https://go.nuxtjs.dev/config-plugins
  plugins: [
  ],

  // Auto import components: https://go.nuxtjs.dev/config-components
  components: true,

  // Modules for dev and build (recommended): https://go.nuxtjs.dev/config-modules
  buildModules: [
    '@nuxtjs/pwa',
  ],

  env: {
    MODE_ENV: process.env.MODE_ENV
  },

  // Axios module configuration: https://go.nuxtjs.dev/config-axios
  axios: {
    // Workaround to avoid enforcing hard-coded localhost:3000: https://github.com/nuxt-community/axios-module/issues/308
    baseURL: (isDev ? 'http://eco-station.tk:8000/get_status' : `${process.env.BASE_URL}:${process.env.BASE_PORT}/${process.env.BASE_ADDR}`),
  },

  // Modules: https://go.nuxtjs.dev/config-modules
  modules: [
    '@nuxtjs/axios'
  ],

  pwa: {
    icon: false, // disables the icon module
    meta: {
      mobileAppIOS: 'true',
      appleStatusBarStyle: 'black-translucent',
      viewport: "initial-scale=1, viewport-fit=cover",
      theme_color: "#001147"
    },
  },

  render: {
    resourceHints: false
  },

  // Build Configuration: https://go.nuxtjs.dev/config-build
  buildDir: 'nuxt-dist',
  build: {
    loaders: {
      sass: {
        implementation: require('sass'),
      },
      scss: {
        implementation: require('sass'),
      },
    },
  }
}
