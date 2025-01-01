<template>
  <div class="post-filter">
    <input 
      v-model="filters.username"
      type="text" 
      placeholder="Username"
      @input="emitFilters"
    >
    <input 
      v-model="filters.email"
      type="text" 
      placeholder="Email"
      @input="emitFilters"
    >
    <select v-model="filters.date_order" @change="emitFilters">
      <option value="">Date order</option>
      <option value="desc">Newest first</option>
      <option value="asc">Oldest first</option>
    </select>
  </div>
</template>

<script>
import '../assets/styles/postfilter.css';

export default {
  data() {
    return {
      filters: {
        username: '',
        email: '',
        date_order: ''
      }
    }
  },
  methods: {
    emitFilters() {
      this.$emit('filter-changed', this.filters);
    }
  }
}
</script>
