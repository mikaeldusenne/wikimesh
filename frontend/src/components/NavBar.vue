<template>
  <nav class="navbar navbar-dark bg-dark">
    <div class="container d-flex flex-wrap justify-content-between gap-2">
      <router-link class="navbar-brand" to="/">WikiMeSH</router-link>
      <div class="d-flex flex-wrap gap-3">
        <router-link class="nav-link text-white" to="/explorer">Explorer</router-link>
        <router-link class="nav-link text-white" to="/methodology">Méthodologie</router-link>
        <router-link class="nav-link text-white" to="/statistics">Statistiques</router-link>
      </div>
    </div>
  </nav>
</template>
