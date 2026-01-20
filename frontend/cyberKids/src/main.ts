import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import { petHintDirective } from './directives/petHint.directive'

const app = createApp(App)
app.use(router)
app.directive('pet-hint', petHintDirective)
app.mount('#app')
