<template>
  <div class="comment">
    <div class="comment-block" :style="levelStyle">
      <!-- Parental comment information -->
      <div v-if="comment.parent_info" class="parent-preview">
        Replying to {{ comment.parent_info.username }}'s comment: "{{ truncatedParentText }}"
      </div>
      <div class="comment-header">
        <img 
          v-if="comment.user.profile && comment.user.profile.photo_url" 
          :src="comment.user.profile.photo_url" 
          :alt="`Profile photo of ${comment.user.username}`" 
          class="profile-photo" 
        />
        <span class="username">{{ comment.user.username }}</span>
        <span class="date">{{ formatDate(comment.created_at) }}</span>
      </div>
      <div class="comment-content">
        <p v-html="sanitizeHTML(comment.text)"></p>
        <div v-if="comment.image" class="image-container">
          <a :href="comment.image" data-lightbox="comment-images" :data-title="comment.text">
            <img :src="comment.image" alt="Comment Image" class="comment-image" />
          </a>
        </div>
        <div v-if="comment.file" class="file-container">
          <a :href="comment.file" class="download-link" target="_blank">
            <i class="fas fa-file-text"></i>
            Download attached file
          </a>
        </div>
        <button @click="toggleReplyForm" class="reply-button">Reply</button>
      </div>
    </div>

    <div class="nested-content" v-if="showReplyForm || hasReplies">
      <div v-if="showReplyForm" class="reply-form-container">
        <p v-if="comment.text" class="replying-to">
          Replying to: "{{ truncatedParentText }}"
        </p>
        <ReplyForm
          :postId="postId"
          :parentId="comment.id"
          @onReplySubmitted="handleReplySubmitted"
          @cancel="showReplyForm = false"
        />
      </div>
      
      <template v-if="comment.replies && comment.replies.length > 0">
        <comment-item
          v-for="reply in comment.replies"
          :key="reply.id"
          :comment="reply"
          :postId="postId"
          @reply-submitted="$emit('reply-submitted')"
        />
      </template>
    </div>
  </div>
</template>

<script>
import ReplyForm from './ReplyForm.vue';
import '../assets/styles/commetitem.css';

export default {
  name: 'CommentItem',
  components: {
    ReplyForm
  },
  props: {
    comment: {
      type: Object,
      required: true
    },
    postId: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      showReplyForm: false
    };
  },
  computed: {
    hasReplies() {
      return this.comment.replies && this.comment.replies.length > 0;
    },
    truncatedParentText() {
      if (this.comment.parent_info && this.comment.parent_info.text) {
        const text = this.comment.parent_info.text;
        return text.length > 30 ? text.substring(0, 30) + '...' : text;
      }
      return '';
    },
    getParentPreview() {
      if (this.comment.parent && typeof this.comment.parent === 'object') {
        const parentText = this.comment.parent.text;
        return parentText.length > 30 ? parentText.substring(0, 30) + '...' : parentText;
      }
      return '';
    },
    levelStyle() {
      const level = this.comment.level || 0;
      const marginLeft = Math.min(level * 40, 200);
      return {
        marginLeft: `${marginLeft}px`,
        width: `calc(100% - ${marginLeft}px)`
      };
    }
  },
  methods: {
    formatDate(dateString) {
      const date = new Date(dateString);
      return `${date.getDate()}.${date.getMonth() + 1}.${date.getFullYear()} at ${date.getHours()}:${date.getMinutes()}`;
    },
    toggleReplyForm() {
      this.showReplyForm = !this.showReplyForm;
    },
    handleReplySubmitted() {
      this.showReplyForm = false;
      this.$emit('reply-submitted');
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
    }
  }
};
</script>

