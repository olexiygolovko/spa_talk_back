<template>
  <div class="auth-container" v-if="!isLoggedIn">
    <div class="auth-buttons">
      <button @click="showRegister = true" class="register-button">Register</button>
      <button @click="showLogin = true" class="login-button">Login</button>
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
          <input 
            v-model="password" 
            type="password" 
            id="password" 
            @input="validatePassword"
            required 
          />
          <div class="password-requirements" :class="{ invalid: !isPasswordValid }">
            Password must contain:
            <ul>
              <li :class="{ valid: hasMinLength }">At least 8 characters</li>
              <li :class="{ valid: hasUpperCase }">At least one uppercase letter</li>
              <li :class="{ valid: hasLowerCase }">At least one lowercase letter</li>
              <li :class="{ valid: hasNumber }">At least one number</li>
              <li :class="{ valid: hasSpecialChar }">At least one special character (!@#$%^&*)</li>
            </ul>
          </div>
        </div>
        <div>
          <label for="home_page">Home Page:</label>
          <input v-model="home_page" type="url" id="home_page" required />
        </div>
        <div>
          <label for="photo">Profile Picture:</label>
          <input 
            type="file" 
            id="photo" 
            ref="photo" 
            @change="handleFileChange" 
            accept="image/*"
          />
        </div>
        <div class="captcha-container">
          <img :src="captchaImage" alt="CAPTCHA" @click="refreshCaptcha" />
          <button type="button" @click="refreshCaptcha" class="refresh-button">
            ↻ Refresh
          </button>
          <input 
            v-model="captcha" 
            type="text" 
            placeholder="Enter captcha text" 
            required 
          />
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
          <label for="login-username">Username:</label>
          <input v-model="username" type="text" id="login-username" required />
        </div>
        <div>
          <label for="login-password">Password:</label>
          <input v-model="password" type="password" id="login-password" required />
        </div>
        <div class="captcha-container">
          <img :src="loginCaptchaImage" alt="CAPTCHA" @click="refreshLoginCaptcha" />
          <button type="button" @click="refreshLoginCaptcha" class="refresh-button">
            ↻ Refresh
          </button>
          <input 
            v-model="loginCaptcha" 
            type="text" 
            placeholder="Enter captcha text" 
            required 
          />
        </div>
        <button type="submit">Login</button>
        <button type="button" @click="cancelLogin">Cancel</button>
      </form>
    </div>
  </div>
  <div v-else>
    <button @click="logout" class="logout-button">Logout</button>
  </div>
</template>

<script>
import axios from 'axios';
import { API_URLS } from '../config/api';
import '../assets/styles/auth.css';

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
      photo: null,
      home_page: '',
      captchaImage: null,
      captcha: '',
      loginCaptchaImage: null,
      loginCaptcha: '',
      hasMinLength: false,
      hasUpperCase: false,
      hasLowerCase: false,
      hasNumber: false,
      hasSpecialChar: false,
    };
  },
  computed: {
    isPasswordValid() {
      return this.hasMinLength && 
             this.hasUpperCase && 
             this.hasLowerCase && 
             this.hasNumber && 
             this.hasSpecialChar;
    }
  },
  methods: {
    handleFileChange(event) {
      const file = event.target.files[0];
      if (file) {
        /* File size check - 5MB limit*/
        if (file.size > 5000000) { // 5MB limit
          alert('File is too large. Please choose a file under 5MB.');
          event.target.value = '';
          return;
        }
        /* Check file type */
        if (!file.type.startsWith('image/')) {
          alert('Please select an image file.');
          event.target.value = '';
          return;
        }
        this.photo = file;
      }
    },

    async loginUser() {
      if (!this.loginCaptcha) {
        alert('Please enter the captcha');
        return;
      }

      try {
        const response = await axios.post(API_URLS.LOGIN, {
          username: this.username,
          password: this.password,
          captcha: this.loginCaptcha.trim()
        }, {
          withCredentials: true,
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
          }
        });

        localStorage.setItem('authToken', response.data.access_token);
        this.$emit('login');
        this.showLogin = false;
        this.clearFields();
        alert('Login successful!');
      } catch (error) {
        console.error("Login error:", error);
        if (error.response?.data?.detail) {
          alert(error.response.data.detail);
          if (error.response.data.detail.includes('captcha')) {
            await this.refreshLoginCaptcha();
            this.loginCaptcha = '';
          }
        } else {
          alert('Login failed, please try again.');
        }
      }
    },

    async registerUser() {
      if (!this.captcha) {
        alert('Please enter the captcha');
        return;
      }

      if (!this.isPasswordValid) {
        alert('Please ensure your password meets all requirements');
        return;
      }

      try {
        const formData = new FormData();
        formData.append('username', this.username);
        formData.append('email', this.email);
        formData.append('password', this.password);
        formData.append('profile.home_page', this.home_page);
        formData.append('captcha', this.captcha.trim());
        
        if (this.photo) {
          formData.append('profile.photo', this.photo);
        }

        const response = await axios.post(API_URLS.REGISTER, formData, {
          withCredentials: true,
          headers: {
            'Accept': 'application/json',
          }
        });

        console.log('Registration response:', response.data);
        alert('Registration successful! You can now log in.');
        this.showRegister = false;
        this.clearFields();
      } catch (error) {
        console.error("Registration error:", error);
        if (error.response?.data?.detail === "Invalid captcha") {
          alert('Invalid captcha, please try again');
          await this.refreshCaptcha();
          this.captcha = '';
        } else {
          alert(`Registration failed: ${error.response?.data?.detail || 'Please ensure your details are correct'}`);
        }
      }
    },

    async refreshCaptcha() {
      try {
        const response = await axios.get(API_URLS.REGISTER, {
          withCredentials: true,
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
          }
        });
        this.captchaImage = response.data.captcha_image;
      } catch (error) {
        console.error('Failed to load registration captcha:', error);
        this.captchaImage = null;
      }
    },

    async refreshLoginCaptcha() {
      try {
        const response = await axios.get(API_URLS.LOGIN, {
          withCredentials: true,
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
          }
        });
        this.loginCaptchaImage = response.data.captcha_image;
      } catch (error) {
        console.error('Failed to load login captcha:', error);
        this.loginCaptchaImage = null;
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
      this.home_page = '';
      this.captcha = '';
      this.loginCaptcha = '';
      this.refreshCaptcha();
      if (this.showLogin) {
        this.refreshLoginCaptcha();
      }
    },

    validatePassword() {
      this.hasMinLength = this.password.length >= 8;
      this.hasUpperCase = /[A-Z]/.test(this.password);
      this.hasLowerCase = /[a-z]/.test(this.password);
      this.hasNumber = /[0-9]/.test(this.password);
      this.hasSpecialChar = /[!@#$%^&*]/.test(this.password);
    },
  },
  watch: {
    showLogin(newVal) {
      if (newVal) {
        this.refreshLoginCaptcha();
      }
    },
    showRegister(newVal) {
      if (newVal) {
        this.refreshCaptcha();
      }
    }
  },
  mounted() {
    if (this.showRegister) {
      this.refreshCaptcha();
    } else if (this.showLogin) {
      this.refreshLoginCaptcha();
    }
  }
};
</script>

