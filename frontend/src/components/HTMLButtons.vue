<template>
  <div class="html-buttons">
    <button type="button" @click="insertTag('<strong></strong>')">B</button>
    <button type="button" @click="insertTag('<i></i>')">I</button>
    <button type="button" @click="insertTag('<a href=\'\'></a>')">URL</button>
    <button type="button" @click="insertTag('<code></code>')">CODE</button>
  </div>
</template>

<script>
import '../assets/styles/htmlbuttons.css';

export default {
  name: 'HtmlButtons',
  methods: {
    insertTag(template) {
      this.$emit('insert-tag', template);
    }
  }
}
</script>
