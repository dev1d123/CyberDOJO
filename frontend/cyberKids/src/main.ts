import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import { petHintDirective } from './directives/petHint.directive'
import VueTour from 'vue3-tour'
import 'vue3-tour/dist/vue3-tour.css'

const app = createApp(App)
app.use(router)
app.use(VueTour)
app.directive('pet-hint', petHintDirective)
app.mount('#app')
