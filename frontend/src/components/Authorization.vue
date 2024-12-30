<template>
  <div>
    <div class="auth-buttons">
      <button v-if="!isLoggedIn" @click="showRegister = true">Register</button>
      <button v-if="!isLoggedIn" @click="showLogin = true">Login</button>
      <button v-if="isLoggedIn" @click="logout">Logout</button>
    </div>

    <!-- Registration form -->
    <div v-if="showRegister" class="register">
      <h2>Register</h2>
      <form @submit.prevent="registerUser" enctype="multipart/form-data">
        <div>
          <label for="username">Username:</label>
          <input v-model="username" type="text" id="username" required />
        </div>
        <div>
          <label for="email">Email:</label>
          <input v-model="email" type="email" id="email" required />
        </div>
        <div>
          <label for="password">Password:</label>
          <input v-model="password" type="password" id="password" required />
        </div>
        <div>
          <label for="photo">Profile Picture:</label>
          <input ref="photo" type="file" id="photo" @change="handleFileChange" />
        </div>
        <button type="submit">Register</button>
        <button type="button" @click="cancelRegister">Cancel</button>
      </form>
    </div>

    <!-- Login form -->
    <div v-if="showLogin" class="login">
      <h2>Login</h2>
      <form @submit.prevent="loginUser">
        <div>
          <label for="username">Username:</label>
          <input v-model="username" type="text" id="username" required />
        </div>
        <div>
          <label for="password">Password:</label>
          <input v-model="password" type="password" id="password" required />
        </div>
        <button type="submit">Login</button>
        <button type="button" @click="cancelLogin">Cancel</button>
      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  props: {
    isLoggedIn: Boolean
  },
  data() {
    return {
      showLogin: false,
      showRegister: false,
      username: '',
      password: '',
      email: '',
      photo: null
    };
  },
  methods: {
    handleFileChange(event) {
      this.photo = event.target.files[0];
    },

    async loginUser() {
      try {
        const response = await axios.post('http://127.0.0.1:8000/api/login/', {
          username: this.username,
          password: this.password
        });
        localStorage.setItem('authToken', response.data.access_token);
        this.$emit('login');
        this.showLogin = false;
        this.clearFields();
        alert('Login successful!');
      } catch (error) {
        console.error("Login error:", error);
        alert('Login failed, please check your credentials.');
      }
    },

    async registerUser() {
      try {
        const formData = new FormData();
        formData.append('username', this.username);
        formData.append('email', this.email);
        formData.append('password', this.password);

        if (this.photo) {
          formData.append('photo', this.photo);
        }

        await axios.post('http://127.0.0.1:8000/api/register/', formData);
        alert('Registration successful! You can now log in.');
        this.showRegister = false;
        this.clearFields();
      } catch (error) {
        console.error("Registration error:", error);
        alert('Registration failed. Please ensure your details are correct and try again.');
      }
    },

    logout() {
      localStorage.removeItem('authToken');
      this.$emit('logout');
      alert('You have been logged out.');
    },

    cancelLogin() {
      this.showLogin = false;
      this.clearFields();
    },

    cancelRegister() {
      this.showRegister = false;
      this.clearFields();
    },

    clearFields() {
      this.username = '';
      this.password = '';
      this.email = '';
      this.photo = null;
    }
  }
};
</script>

<style scoped>
.auth-buttons button {
  margin-right: 10px;
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.auth-buttons button:hover {
  background-color: #0056b3;
}

form {
  margin-top: 20px;
}

form div {
  margin-bottom: 15px;
}

form label {
  display: block;
  font-weight: bold;
}

form input {
  width: 100%;
  padding: 8px;
  font-size: 14px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

form button {
  margin-top: 10px;
  padding: 10px 20px;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

form button:hover {
  background-color: #218838;
}

form button[type="button"] {
  background-color: #dc3545;
}

form button[type="button"]:hover {
  background-color: #c82333;
}
</style>
