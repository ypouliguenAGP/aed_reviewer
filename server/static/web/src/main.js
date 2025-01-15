import './assets/main.css'
import "bootstrap/dist/css/bootstrap.min.css"
import "bootstrap"
import {
    BIconArrowDown,
    BIconArrowUp,
  } from "bootstrap-icons-vue";


import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
app.component("BIconArrowDown", BIconArrowDown);
app.component("BIconArrowUp", BIconArrowUp);