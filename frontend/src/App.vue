<template>
  <NavBar />
  <main class="container py-4"><router-view /></main>
</template>

<script setup lang="ts">
import NavBar from "@/components/NavBar.vue";
</script>

<style>
body { background: #f7f7f7; color: #2c3e50; }
a { color: #333; }
.router-link-active { font-weight: 600; }
</style>
