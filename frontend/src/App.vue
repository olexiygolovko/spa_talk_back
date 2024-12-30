<template>
  <div id="app">
    <Authorization :isLoggedIn="isLoggedIn" @login="handleLogin" @logout="handleLogout"/>
    <Posts v-if="isLoggedIn" />
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import Authorization from './components/Authorization.vue';
import Posts from './components/Posts.vue';

export default {
  components: {
    Authorization,
    Posts
  },
  setup() {
    const isLoggedIn = ref(false);

    const handleLogin = () => {
      isLoggedIn.value = true;
    };

    const handleLogout = () => {
      isLoggedIn.value = false;
      localStorage.removeItem('authToken'); // Remove token
    };

    onMounted(() => {
      const token = localStorage.getItem('authToken');
      if (token) {
        isLoggedIn.value = true;
      }
    });

    return { isLoggedIn, handleLogin, handleLogout };
  }
};
</script>
