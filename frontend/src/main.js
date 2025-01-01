import { createApp } from 'vue'
import App from './App.vue'
import './assets/styles/main.css'

// Configure lightbox
document.addEventListener('DOMContentLoaded', () => {
  if (window.lightbox) {
    lightbox.option({
      'resizeDuration': 200,
      'wrapAround': true,
      'albumLabel': 'Image %1 of %2'
    });
  }
});

createApp(App).mount('#app')
