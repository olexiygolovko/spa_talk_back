<template>
  <form @submit.prevent="submitReply" class="reply-form">
    <HtmlButtons @insert-tag="insertTag" />
    <textarea 
      v-model="replyText" 
      placeholder="Write a reply..." 
      ref="replyTextarea"
      required
    ></textarea>
    <div class="form-group">
      <label for="image">Image (max 320x240px, JPG/GIF/PNG):</label>
      <input 
        type="file" 
        ref="image" 
        @change="handleFileChange('image', $event)" 
        accept="image/jpeg,image/png,image/gif"
      />
    </div>
    <div v-if="replyData.image" class="image-preview">
      <img :src="getMediaUrl(replyData.image)" alt="Image preview" />
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
    <div class="form-buttons">
      <button type="submit" class="post-reply-button">Post Reply</button>
      <button type="button" @click="$emit('cancel')" class="cancel-button">Cancel</button>
    </div>
  </form>
</template>

<script>
import '../assets/styles/replyform.css';
import axios from 'axios';
import HtmlButtons from './HTMLButtons.vue';
import { API_URLS } from '../config/api';

export default {
  components: {
    HtmlButtons
  },
  props: ['postId', 'parentId'],
  data() {
    return {
      replyText: '',
      replyData: {
        image: null,
        file: null
      }
    };
  },
  methods: {
    insertTag(template) {
      const textarea = this.$refs.replyTextarea;
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const text = this.replyText;
      const before = text.substring(0, start);
      const selection = text.substring(start, end);
      const after = text.substring(end);
      
      if (template.includes('href')) {
        this.replyText = before + template + after;
        textarea.focus();
        const newCursor = start + template.indexOf('href') + 6;
        textarea.setSelectionRange(newCursor, newCursor);
      } else {
        const closingTagIndex = template.indexOf('</');
        const newText = before + template.substring(0, closingTagIndex) + 
                       selection + template.substring(closingTagIndex) + after;
        this.replyText = newText;
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

    handleFileChange(field, event) {
      const file = event.target.files[0];
      if (field === 'image') {
        if (file.size > 320 * 240) {
          alert('Image size should not exceed 320x240 pixels');
          this.$refs.image.value = null;
          return;
        }
        if (!['image/jpeg', 'image/png', 'image/gif'].includes(file.type)) {
          alert('Only JPG, PNG, and GIF formats are allowed');
          this.$refs.image.value = null;
          return;
        }
      } else if (field === 'file') {
        if (file.size > 100 * 1024) {
          alert('File size should not exceed 100KB');
          this.$refs.file.value = null;
          return;
        }
        if (file.type !== 'text/plain') {
          alert('Only TXT format is allowed');
          this.$refs.file.value = null;
          return;
        }
      }
      this.replyData[field] = file;
    },

    async submitReply() {
      const token = localStorage.getItem("authToken");
      if (!token) {
        alert("You are not authenticated. Please log in first.");
        return;
      }

      const formData = new FormData();
      formData.append('post', this.postId);
      formData.append('text', this.replyText);
      formData.append('parent', this.parentId);
      if (this.replyData.image) {
        formData.append('image', this.replyData.image);
      }
      if (this.replyData.file) {
        formData.append('file', this.replyData.file);
      }

      try {
        const response = await axios.post(API_URLS.COMMENTS, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
            Authorization: `Bearer ${token}`,
          },
        });
        
        this.replyText = '';
        this.replyData.image = null;
        this.replyData.file = null;
        this.$emit('onReplySubmitted');
      } catch (error) {
        console.error("Error submitting reply:", error);
        if (error.response?.status === 401) {
          alert("Authentication error. Please log in again.");
        } else {
          alert("Failed to submit reply, please try again.");
        }
      }
    },

    getMediaUrl(path) {
      if (!path || typeof path !== 'string') return '';

      try {
        const url = new URL(path);
        return path;
      } catch (e) {
        const basePath = process.env.NODE_ENV === 'production'
          ? 'https://spa-talk-back.onrender.com'
          : 'http://127.0.0.1:8000';
        
        const mediaPath = path.startsWith('/media/') ? path : `/media/${path.replace(/^\//, '')}`;
        return `${basePath}${mediaPath}`;
      }
    }
  }
};
</script>
