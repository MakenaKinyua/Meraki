import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { VueQueryPlugin } from '@tanstack/vue-query'
import App from './App.vue'
import { queryClient } from './lib/query-client'
import './style.css'

createApp(App)
  .use(createPinia())
  .use(VueQueryPlugin, { queryClient })
  .mount('#app')
