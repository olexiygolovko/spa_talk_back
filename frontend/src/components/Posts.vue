<template>
  <div>
    <!-- Panel with a post creation button and filters -->
    <div class="posts-header">
      <button @click="showCreatePostForm = true" v-if="!showCreatePostForm" class="create-post-button">
        Create New Post
      </button>
      <PostFilter @filter-changed="handleFilterChange" />
    </div>

    <!-- Form for creating a post -->
    <div v-if="showCreatePostForm" class="create-post">
      <h2>Create Post</h2>
      <form @submit.prevent="validateAndCreatePost">
        <div class="form-group">
          <HtmlButtons @insert-tag="insertTag" />
          <textarea
            v-model="newPost.text"
            id="text"
            ref="postTextarea"
            placeholder="Write something..."
            required
          ></textarea>
        </div>
        <div class="form-group">
          <label for="image">Image (max 320x240px, JPG/GIF/PNG):</label>
          <input 
            type="file" 
            ref="image" 
            @change="handleFileChange('image', $event)" 
            accept="image/jpeg,image/png,image/gif"
          />
        </div>
        <div class="form-group">
          <label for="file">File (max 100KB, TXT only):</label>
          <input 
            type="file" 
            ref="file" 
            @change="handleFileChange('file', $event)" 
            accept=".txt"
          />
        </div>
        <button type="submit">Create Post</button>
        <button type="button" @click="showCreatePostForm = false" class="cancel-button">Cancel</button>
      </form>
    </div>

    <!-- Список постов -->
    <div v-for="post in posts" :key="post.id" class="post">
      <div class="post-header">
        <div class="post-header-left">
          <img v-if="post.user.profile && post.user.profile.photo_url" 
               :src="post.user.profile.photo_url" 
               :alt="`Profile photo of ${post.user.username}`" 
               class="profile-photo" />
          <h3>{{ post.user.username }} {{ formatDate(post.created_at) }}</h3>
        </div>
        <div class="post-header-right">
          <h4 @click="() => toggleComments(post.id)" class="comments-toggle">
            Comments {{ isCommentsVisible(post.id) ? '⬆' : '⬇' }} ({{ post.comments_count }})
          </h4>
        </div>
      </div>
      <p v-html="sanitizeHTML(post.text)"></p>
      <div v-if="post.image" class="image-container">
        <a :href="post.image" data-lightbox="post-images" :data-title="post.text">
          <img :src="post.image" alt="Post Image" class="post-image" />
        </a>
      </div>
      <div v-if="post.file" class="file-container">
        <a :href="post.file" class="download-link" target="_blank">
          <i class="fas fa-file-text"></i>
          Download attached file
        </a>
      </div>
      <Comments 
        :postId="post.id" 
        :isVisible="isCommentsVisible(post.id)"
        @visibility-changed="(visible) => updateCommentsVisibility(post.id, visible)"
      />
    </div>

    <!-- Pagination -->
    <div class="pagination">
      <button @click="fetchPosts(previous)" :disabled="!previous">Previous</button>
      <button @click="fetchPosts(next)" :disabled="!next">Next</button>
    </div>
  </div>
</template>

<script>
import '../assets/styles/posts.css';
import axios from "axios";
import Comments from "./Comments.vue";
import HtmlButtons from './HTMLButtons.vue';  // Changed name format
import PostFilter from './PostFilter.vue';

export default {
  data() {
    return {
      posts: [],
      newPost: {
        text: "",
        image: null,
        file: null,
      },
      showCreatePostForm: false,
      next: null,
      previous: null,
      commentsVisibility: {},  // Add a dictionary to store comments visibility
      activeFilters: {
        username: '',
        email: '',
        date_order: ''
      }
    };
  },
  components: {
    Comments,
    HtmlButtons,  // Changed name format
    PostFilter
  },
  created() {
    this.fetchPosts();
  },
  methods: {
    handleFilterChange(filters) {
      this.activeFilters = filters;
      this.fetchPosts(); // Fetch posts with new filters
    },
    fetchPosts(url = "http://127.0.0.1:8000/api/posts/") {
      const token = localStorage.getItem("authToken");
      if (!token) {
        alert("You are not authenticated. Please log in first.");
        return;
      }

      // Add filters to the URL query string
      const params = new URLSearchParams();
      if (this.activeFilters.username) params.append('username', this.activeFilters.username);
      if (this.activeFilters.email) params.append('email', this.activeFilters.email);
      if (this.activeFilters.date_order) params.append('date_order', this.activeFilters.date_order);

      // if url already has query params, append new params with '&'
      const finalUrl = url.includes('?') 
        ? `${url}&${params.toString()}`
        : `${url}?${params.toString()}`;

      axios
        .get(finalUrl, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })
        .then((response) => {
          this.posts = response.data.results;
          this.next = response.data.next;
          this.previous = response.data.previous;
        })
        .catch((error) => {
          console.error("Error fetching posts:", error);
          if (error.response?.status === 401) {
            alert("Authentication error. Please log in again.");
          }
        });
    },
    handleFileChange(field, event) {
      const file = event.target.files[0];
      if (!file) return;

      if (field === 'image') {
        if (!file.type.match('image.*')) {
          alert('Please select an image file (JPG, GIF, or PNG)');
          event.target.value = '';
          return;
        }
      } else if (field === 'file') {
        if (file.type !== 'text/plain') {
          alert('Please select a TXT file');
          event.target.value = '';
          return;
        }
        if (file.size > 102400) { // 100KB
          alert('File size must be less than 100KB');
          event.target.value = '';
          return;
        }
      }
      this.newPost[field] = file;
    },
    createPost() {
      const token = localStorage.getItem("authToken");
      if (!token) {
        alert("You are not authenticated. Please log in first.");
        return;
      }

      const formData = new FormData();
      formData.append("text", this.newPost.text);

      if (this.newPost.image) {
        formData.append("image", this.newPost.image);
      }

      if (this.newPost.file) {
        formData.append("file", this.newPost.file);
      }

      axios
        .post("http://127.0.0.1:8000/api/posts/", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
            Authorization: `Bearer ${token}`,
          },
        })
        .then((response) => {
          this.posts.unshift(response.data); // Add the new post to the beginning of the list
          this.newPost.text = "";
          this.newPost.image = null;
          this.newPost.file = null;
          this.showCreatePostForm = false; // Hide the form after submission
        })
        .catch((error) => {
          console.error("Error creating post:", error);
          if (error.response?.status === 401) {
            alert("Authentication error. Please log in again.");
          } else {
            alert("Failed to create post, please try again.");
          }
        });
    },
    insertTag(template) {
      const textarea = this.$refs.postTextarea;
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const text = this.newPost.text;
      const before = text.substring(0, start);
      const selection = text.substring(start, end);
      const after = text.substring(end);
      
      if (template.includes('href')) {
        this.newPost.text = before + template + after;
        textarea.focus();
        const newCursor = start + template.indexOf('href') + 6;
        textarea.setSelectionRange(newCursor, newCursor);
      } else {
        const closingTagIndex = template.indexOf('</');
        const newText = before + template.substring(0, closingTagIndex) + 
                       selection + template.substring(closingTagIndex) + after;
        this.newPost.text = newText;
        textarea.focus();
      }
    },

    validateHTML(text) {
      const parser = new DOMParser();
      const doc = parser.parseFromString(`<div>${text}</div>`, 'application/xml');
      const parseError = doc.getElementsByTagName('parsererror');
      if (parseError.length > 0) {
        throw new Error('Invalid HTML: Please ensure all tags are properly closed');
      }
      
      // Check if the tags are allowed
      const allowedTags = ['a', 'code', 'i', 'strong'];
      const div = document.createElement('div');
      div.innerHTML = text;
      
      const findTags = (element) => {
        Array.from(element.children).forEach(child => {
          if (!allowedTags.includes(child.tagName.toLowerCase())) {
            throw new Error(`Tag <${child.tagName.toLowerCase()}> is not allowed`);
          }
          if (child.children.length) {
            findTags(child);
          }
        });
      };
      
      findTags(div);
      return text;
    },

    validateAndCreatePost() {
      try {
        this.validateHTML(this.newPost.text);
        this.createPost();
      } catch (error) {
        alert(error.message);
      }
    },
    sanitizeHTML(html) {
      const div = document.createElement('div');
      div.innerHTML = html;
      
      const links = div.getElementsByTagName('a');
      for (let link of links) {
        link.setAttribute('target', '_blank');
        link.setAttribute('rel', 'noopener noreferrer');
      }
      
      return div.innerHTML;
    },
    formatDate(dateString) {
      const date = new Date(dateString);
      const day = String(date.getDate()).padStart(2, '0');
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const year = date.getFullYear();
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      return `${day}.${month}.${year} at ${hours}:${minutes}`;
    },
    toggleComments(postId) {
      this.commentsVisibility[postId] = !this.isCommentsVisible(postId);
    },
    isCommentsVisible(postId) {
      return !!this.commentsVisibility[postId];
    },
    updateCommentsVisibility(postId, visible) {
      this.commentsVisibility[postId] = visible;
    }
  },
};
</script>
