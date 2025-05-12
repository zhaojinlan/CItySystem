import { createApp } from 'vue'; // Correct Vue 3 import
import App from './App.vue';
import router from './router'; // Ensure vue-router@4 is installed

const app = createApp(App);

app.use(router); // Register router plugin

app.mount('#app');