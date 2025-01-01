<template>
  <div class="comments-container">
    <div class="comments-header">
      <div></div>
      <button @click="showAddComment" v-if="!showCommentForm" class="add-comment-button">Add Comment</button>
    </div>
    <div v-if="isVisible">
      <form v-if="showCommentForm" @submit.prevent="validateAndSubmit" class="comment-form">
        <HtmlButtons @insert-tag="insertTag" />
        <textarea 
          v-model="commentText" 
          placeholder="Add a comment"
          ref="commentTextarea"
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
          <button type="submit" class="post-comment-button">Post Comment</button>
          <button type="button" @click="showCommentForm = false" class="cancel-button">Cancel</button>
        </div>
      </form>
      <div class="comments-list">
        <comment-item
          v-for="comment in rootComments"
          :key="comment.id"
          :comment="comment"
          :postId="postId"
          @reply-submitted="fetchComments"
        />
      </div>
    </div>
  </div>
</template>

<script>
import axiosInstance from '../config/api';
import '../assets/styles/comments.css';
import CommentItem from './CommentItem.vue';
import HtmlButtons from './HTMLButtons.vue';
import { API_URLS } from '../config/api';

export default {
  props: {
    postId: {
      type: Number,
      required: true
    },
    isVisible: {
      type: Boolean,
      default: false
    }
  },
  components: {
    CommentItem,
    HtmlButtons
  },
  data() {
    return {
      comments: [],
      commentText: '',
      showCommentForm: false,
      showComments: false,
      replyToId: null,
      commentData: {
        text: '',
        image: null,
        file: null
      }
    };
  },
  created() {
    this.fetchComments();
  },
  computed: {
    rootComments() {
      return this.comments.filter(comment => !comment.parent);
    }
  },
  watch: {
    isVisible(newValue) {
      this.showComments = newValue;
    },
    showComments(newValue) {
      this.$emit('visibility-changed', newValue);
    },
    comments: {
      handler(newComments) {
        this.$emit('update-count', newComments.length);
      },
      deep: true
    }
  },
  methods: {
    async fetchComments() {
      try {
        const response = await axiosInstance.get(`/posts/${this.postId}/comments/`);
        this.comments = response.data;
        // Update the count after the comments have been fetched
        this.$nextTick(() => {
          this.$emit('update-count', this.comments.length);
        });
      } catch (error) {
        console.error("Error fetching comments:", error);
        this.comments = [];
        this.$emit('update-count', 0);
        if (error.response?.status === 401) {
          alert("Authentication error. Please log in again.");
        }
      }
    },

    async createComment() {
      const token = localStorage.getItem("authToken");
      if (!token) {
        alert("You are not authenticated. Please log in first.");
        return;
      }

      try {
        const response = await axiosInstance.post(API_URLS.COMMENTS, {
          post: this.postId,
          text: this.commentText
        }, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        this.commentText = '';
        this.showCommentForm = false; // Hide the form after submission
        this.fetchComments(); // This will update the comments list
      } catch (error) {
        console.error("Error submitting comment:", error);
        if (error.response?.status === 401) {
          alert("Authentication error. Please log in again.");
        } else {
          alert("Failed to submit comment, please try again.");
        }
      }
    },

    async replyToComment() {
      const token = localStorage.getItem("authToken");
      if (!token) {
        alert("You are not authenticated. Please log in first.");
        return;
      }

      try {
        const response = await axiosInstance.post(API_URLS.COMMENTS, {
          post: this.postId,
          text: this.commentText
        }, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        this.commentText = '';
        this.showCommentForm = false; // Hide the form after submission
        this.fetchComments(); // This will update the comments list
      } catch (error) {
        console.error("Error submitting comment:", error);
        if (error.response?.status === 401) {
          alert("Authentication error. Please log in again.");
        } else {
          alert("Failed to submit comment, please try again.");
        }
      }
    },

    async submitComment() {
      const token = localStorage.getItem("authToken");
      if (!token) {
        alert("You are not authenticated. Please log in first.");
        return;
      }

      const formData = new FormData();
      formData.append('post', this.postId);
      formData.append('text', this.commentText);
      if (this.commentData.image) {
        formData.append('image', this.commentData.image);
      }
      if (this.commentData.file) {
        formData.append('file', this.commentData.file);
      }
      if (this.replyToId) {
        formData.append('parent', this.replyToId);
      }

      try {
        const response = await axiosInstance.post(API_URLS.COMMENTS, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
            Authorization: `Bearer ${token}`,
          },
        });
        this.commentText = '';
        this.commentData.image = null;
        this.commentData.file = null;
        this.showCommentForm = false;
        this.replyToId = null;
        this.fetchComments();
      } catch (error) {
        console.error("Error submitting comment:", error);
        if (error.response?.status === 401) {
          alert("Authentication error. Please log in again.");
        } else {
          alert("Failed to submit comment, please try again.");
        }
      }
    },

    showReplyForm(commentId) {
      this.replyToId = commentId; 
      this.showCommentForm = true;
    },

    showReplyForm(index) {
      try {
        this.replyFormIndex = index;
      } catch (error) {
        console.error("Error showing reply form:", error);
      }
    },
    hideReplyForm() {
      this.replyFormIndex = null;
    },
    handleReplySubmitted() {
      this.hideReplyForm();
      this.fetchComments();
    },
    toggleCommentVisibility(index) {
      this.$set(this.visibleComments, index, !this.visibleComments[index]);
    },
    toggleCommentsVisibility() {
      this.showComments = !this.showComments;
    },
    showAddComment() {
      this.showCommentForm = true;
      this.showComments = true; // Show comments when adding a new comment
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
    handleImageError(comment) {
      console.error(`Error loading profile photo for user: ${comment.user.username}`);
    },
    insertTag(template) {
      const textarea = this.$refs.commentTextarea;
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const text = this.commentText;
      const before = text.substring(0, start);
      const selection = text.substring(start, end);
      const after = text.substring(end);
      
      if (template.includes('href')) {
        this.commentText = before + template + after;
        textarea.focus();
        const newCursor = start + template.indexOf('href') + 6;
        textarea.setSelectionRange(newCursor, newCursor);
      } else {
        const closingTagIndex = template.indexOf('</');
        const newText = before + template.substring(0, closingTagIndex) + 
                       selection + template.substring(closingTagIndex) + after;
        this.commentText = newText;
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

    validateAndSubmit() {
      try {
        this.validateHTML(this.commentText);
        this.submitComment();
      } catch (error) {
        alert(error.message);
      }
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
      this.commentData[field] = file;
    }
  }
};
</script>