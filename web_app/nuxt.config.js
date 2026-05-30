export default {
  ssr: true,

  pwa: {
    meta: {
      title: 'eco-energo',
      author: 'ООО "ЭКО-ЭНЕРГО',
    },
    manifest: {
      name: process.env.API_SERVER_NAME,
      short_name: process.env.API_SERVER_NAME,
      orientation: 'portrait',
      description: 'description',
      icons: [
        {
          "src": "/icon/apple-touch-icon-32x32.png",
          "sizes": "32x32",
          "type": "image/png"
        },
        {
          "src": "/icon/apple-touch-icon-72x72.png",
          "sizes": "72x72",
          "type": "image/png"
        },
        {
          "src": "/icon/apple-touch-icon-76x76.png",
          "sizes": "76x76",
          "type": "image/png"
        },
        {
          "src": "/icon/apple-touch-icon-114x114.png",
          "sizes": "114x114",
          "type": "image/png"
        },
        {
          "src": "/icon/apple-touch-icon-120x120.png",
          "sizes": "120x120",
          "type": "image/png"
        },
        {
          "src": "/icon/apple-touch-icon-144x144.png",
          "sizes": "144x144",
          "type": "image/png"
        },
        {
          "src": "/icon/apple-touch-icon-152x152.png",
          "sizes": "152x152",
          "type": "image/png"
        },
        {
          "src": "/icon/apple-touch-icon-180x180.png",
          "sizes": "180x180",
          "type": "image/png",
          "purpose": "any maskable"
        },
      ],
      display: 'standalone',
      background_color: '#001147',
      theme_color: '#001147',
      start_url: `https://${process.env.API_SERVER_NAME}`,
      lang: 'ru-RU',
      useWebmanifestExtension: false
    },
  },

  loading: '~/components/loading.vue',

  // Global page headers: https://go.nuxtjs.dev/config-head
  head: {
    title: process.env.API_SERVER_NAME,
    htmlAttrs: {
      lang: 'ru-RU',
      manifest: "default.appcache"
    },
    noscript: [{ innerHTML: "У вас отключен JavaScript. Сайт может отображаться некорректно. Рекомендуем включить JavaScript." }],
    meta: [
      { charset: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0' },
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
      { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' },
      { rel: "apple-touch-startup-image", href: "/static/icon/apple-touch-icon.png" },
      { rel: "apple-touch-icon", href: "/static/icon/apple-touch-icon.png" },
      { rel: "apple-touch-icon", sizes: "72x72", href: "/static/icon/apple-touch-icon-72x72.png" },
      { rel: "apple-touch-icon", sizes: "114x114", href: "/static/icon/apple-touch-icon-114x114.png" },
      { rel: "apple-touch-icon", sizes: "144x144", href: "/static/icon/apple-touch-icon-144x144.png" }
    ],
  },

  // Global CSS: https://go.nuxtjs.dev/config-css
  css: [
    '~assets/css/reset.css',
    '~assets/fonts/main.css',
    { src: '~assets/scss/main.scss', lang: 'scss' }
  ],

  // router: {
  //   linkActiveClass: 'active'
  // },

  // Plugins to run before rendering page: https://go.nuxtjs.dev/config-plugins
  plugins: [
    { src: '~/plugins/chart.js', mode: 'client'},
    { src: '~/plugins/ymapPlugin.js', mode: 'client' }
  ],

  // Auto import components: https://go.nuxtjs.dev/config-components
  components: true,

  // Modules for dev and build (recommended): https://go.nuxtjs.dev/config-modules
  buildModules: [
    '~/modules/ws',
    "@nuxtjs/svg",
    '@nuxtjs/dotenv',
  ],

  // Modules: https://go.nuxtjs.dev/config-modules
  modules: [
    'cookie-universal-nuxt',
    '@nuxtjs/axios',
    '~/modules/ws',
  ],

  websocket: {
    url: process.env.API_WSS,
    debugSocket: false,
  },

  // Build Configuration: https://go.nuxtjs.dev/config-build
  build: {
    loaders: {
      sass: {
        implementation: require('sass'),
      },
      scss: {
        implementation: require('sass'),
      },
    },
    src: "nuxt.config.js",
    use: "@nuxtjs/now-builder",
    config: {
      serverFiles: ["package.json"]
    },
    extend (config) {
      config.node = {
        fs: "empty"
      }
    }
  },

  axios: {
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
    },
  },

  router: {
    middleware: [
     'needAuth',
    ],
    extendRoutes(_routes, resolve) {
      return [
        {
          name: 'index',
          path: '/',
          component: resolve(__dirname, 'pages/index.vue'),
          chunkName: 'pages/index'
        },
        {
          name: 'index-fail',
          path: '/index',
          component: resolve(__dirname, 'pages/index-fail.vue'),
          chunkName: 'pages/index-fail'
        },
        {
          name: 'profile',
          path: '/profile',
          component: resolve(__dirname, 'pages/profile/index.vue'),
          chunkName: 'pages/profile/index'
        },
        {
          name: 'pay-success',
          path: '/profile/pay-success',
          component: resolve(__dirname, 'pages/profile/index.vue'),
          chunkName: 'pages/profile/index'
        },
        {
          name: 'pay-fail',
          path: '/profile/pay-fail',
          component: resolve(__dirname, 'pages/profile/index.vue'),
          chunkName: 'pages/profile/index'
        },
          // exp
        {
          name: 'payment',
          path: '/payment',
          component: resolve(__dirname, 'pages/payment/index.vue'),
          chunkName: 'pages/payment/index'
        },
          // end exp
        {
          name: 'profile/edit',
          path: '/profile/edit',
          component: resolve(__dirname, 'pages/profile/edit.vue'),
          chunkName: 'pages/profile/edit'
        },
        {
          name: 'refills',
          path: '/refills',
          component: resolve(__dirname, 'pages/refill.vue'),
          chunkName: 'pages/refill',
          children: [{
            name: "refill",
            path: "/refill",
            component: resolve(__dirname, 'pages/refill/index.vue'),
          },
          {
            name: 'map',
            path: "/refill/map",
            component: resolve(__dirname, 'pages/refill/map.vue'),
            chunkName: 'pages/refill/map'
          }]
        },
        {
          name: 'history',
          path: '/history',
          component: resolve(__dirname, 'pages/history.vue'),
          chunkName: 'pages/history',
          children: [{
            name: "session",
            path: "/history",
            component: resolve(__dirname, 'pages/history/index.vue'),
          },
          {
            name: 'transaction',
            path: "/history/transaction",
            component: resolve(__dirname, 'pages/history/transaction.vue'),
            chunkName: 'pages/history/transaction'
          }]
        },
        {
          name: 'spaces/:id',
          path: '/spaces/:id',
          component: resolve(__dirname, 'pages/spaces/_id.vue'),
          chunkName: 'pages/spaces/_id'
        },
        {
          name: 'spaces',
          path: '/spaces',
          component: resolve(__dirname, 'pages/profile/index.vue'),
          chunkName: 'pages/profile/index'
        },
      ]
    }
  },

  routes: [
    { src: "/_nuxt/.+", "headers": { "Cache-Control": "max-age=31557600" } },
    {
      src: "/sw.js",
      dest: "/_nuxt/static/sw.js",
      headers: {
        "cache-control": "public, max-age=43200, immutable",
        "Service-Worker-Allowed": "/"
      }
    },
    { src: "/(.*)", "dist": "/" }
  ]
}
