<template>
  <form @submit.prevent="submitReply" class="reply-form">
    <HtmlButtons @insert-tag="insertTag" />
    <textarea 
      v-model="replyText" 
      placeholder="Write a reply..." 
      ref="replyTextarea"
      required
    ></textarea>
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

export default {
  components: {
    HtmlButtons
  },
  props: ['postId', 'parentId'],
  data() {
    return {
      replyText: ''
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

    submitReply() {
      try {
        this.validateHTML(this.replyText);
        const token = localStorage.getItem("authToken");
        if (!token) {
          alert("You are not authenticated. Please log in first.");
          return;
        }

        axios.post('http://127.0.0.1:8000/api/comments/', {
          post: this.postId,
          text: this.replyText,
          parent: this.parentId
        }, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })
        .then(response => {
          this.replyText = '';
          this.$emit('onReplySubmitted');
        })
        .catch(error => {
          console.error("Error submitting reply:", error);
          if (error.response?.status === 401) {
            alert("Authentication error. Please log in again.");
          } else {
            alert("Failed to submit reply, please try again.");
          }
        });
      } catch (error) {
        alert(error.message);
      }
    }
  }
};
</script>
