<template>
  <div>
    <h4>Comments</h4>
    <div v-for="comment in comments" :key="comment.id">
      <p>{{ comment.user.username }}: {{ comment.text }}</p>
    </div>
    <form @submit.prevent="submitComment">
      <textarea v-model="commentText" placeholder="Add a comment"></textarea>
      <button type="submit">Post Comment</button>
    </form>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  props: ['postId'],
  data() {
    return {
      comments: [],
      commentText: ''
    };
  },
  created() {
    this.fetchComments();
  },
  methods: {
    fetchComments() {
      const token = localStorage.getItem("authToken");
      if (!token) {
        alert("You are not authenticated. Please log in first.");
        return;
      }

      axios.get(`http://127.0.0.1:8000/api/posts/${this.postId}/comments/`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
        .then(response => {
          this.comments = response.data;
        })
        .catch(error => {
          console.error("Error fetching comments:", error);
          if (error.response?.status === 401) {
            alert("Authentication error. Please log in again.");
          }
        });
    },
    submitComment() {
      const token = localStorage.getItem("authToken");
      if (!token) {
        alert("You are not authenticated. Please log in first.");
        return;
      }

      axios.post('http://127.0.0.1:8000/api/comments/', {
        post: this.postId,
        text: this.commentText
      }, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
        .then(response => {
          this.commentText = '';
          this.fetchComments();
        })
        .catch(error => {
          console.error("Error submitting comment:", error);
          if (error.response?.status === 401) {
            alert("Authentication error. Please log in again.");
          } else {
            alert("Failed to submit comment, please try again.");
          }
        });
    }
  }
};
</script>
