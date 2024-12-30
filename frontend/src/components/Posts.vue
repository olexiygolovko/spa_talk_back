<template>
  <div>
    <!-- Форма для создания поста -->
    <div class="create-post">
      <h2>Create Post</h2>
      <form @submit.prevent="createPost">
        <div class="form-group">
          <label for="text">Text:</label>
          <textarea
            v-model="newPost.text"
            id="text"
            placeholder="Write something..."
            required
          ></textarea>
        </div>
        <div class="form-group">
          <label for="image">Image:</label>
          <input type="file" ref="image" @change="handleFileChange('image', $event)" />
        </div>
        <div class="form-group">
          <label for="file">File:</label>
          <input type="file" ref="file" @change="handleFileChange('file', $event)" />
        </div>
        <button type="submit">Create Post</button>
      </form>
    </div>

    <!-- Posts list -->
    <div v-for="post in posts" :key="post.id" class="post">
      <h3>{{ post.user.username }} - {{ post.created_at }}</h3>
      <p>{{ post.text }}</p>
      <div v-if="post.image">
        <img
          :src="`http://127.0.0.1:8000${post.image}`"
          alt="Post Image"
          class="post-image"
        />
      </div>
      <div v-if="post.file">
        <a
          :href="`http://127.0.0.1:8000${post.file}`"
          target="_blank"
          class="download-link"
        >
          Download file
        </a>
      </div>
      <Comments :postId="post.id" />
    </div>
  </div>
</template>

<script>
import axios from "axios";
import Comments from "./Comments.vue";

export default {
  data() {
    return {
      posts: [],
      newPost: {
        text: "",
        image: null,
        file: null,
      },
    };
  },
  components: {
    Comments,
  },
  created() {
    this.fetchPosts();
  },
  methods: {
    fetchPosts() {
      const token = localStorage.getItem("authToken");
      if (!token) {
        alert("You are not authenticated. Please log in first.");
        return;
      }

      axios
        .get("http://127.0.0.1:8000/api/posts/", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })
        .then((response) => {
          this.posts = response.data;
        })
        .catch((error) => {
          console.error("Error fetching posts:", error);
          if (error.response?.status === 401) {
            alert("Authentication error. Please log in again.");
          }
        });
    },
    handleFileChange(field, event) {
      this.newPost[field] = event.target.files[0];
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
          this.posts.unshift(response.data); // add new post to the top
          this.newPost.text = "";
          this.newPost.image = null;
          this.newPost.file = null;
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
  },
};
</script>

<style scoped>
.create-post {
  margin-bottom: 20px;
}

.create-post .form-group {
  margin-bottom: 15px;
}

.create-post label {
  display: block;
  font-weight: bold;
}

.create-post textarea {
  width: 100%;
  padding: 10px;
  font-size: 14px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

.create-post input[type="file"] {
  margin-top: 5px;
}

.create-post button {
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.create-post button:hover {
  background-color: #0056b3;
}

.post {
  border: 1px solid #ddd;
  padding: 20px;
  margin-bottom: 20px;
  border-radius: 5px;
}

.post h3 {
  margin: 0 0 10px;
  font-size: 18px;
}

.post .post-image {
  max-width: 100%;
  height: auto;
}

.post .download-link {
  display: block;
  margin-top: 10px;
  font-size: 14px;
  color: #007bff;
}

.post .download-link:hover {
  text-decoration: underline;
}
</style>
