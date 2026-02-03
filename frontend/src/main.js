import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router' // Importa nosso router

const app = createApp(App)
app.use(router) // Avisa o Vue para usar o Router
app.mount('#app')