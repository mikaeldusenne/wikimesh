<template>
  <section class="py-4">
    <h1>WikiMeSH</h1>
    <p class="lead">Outil de recherche des entrées Wikipédia correspondant aux concepts MeSH.</p>
    <div class="row g-3 mt-3">
      <div v-for="[to, label] in links" :key="to" class="col-md-4">
        <router-link class="btn btn-secondary w-100 py-4 fw-bold" :to="to">{{ label }} »</router-link>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
const links = [["/explorer", "Explorer"], ["/methodology", "Méthodologie"], ["/statistics", "Statistiques"]] as const;
</script>
