<template>
  <div class="jumbotron">
    <div class="container">
      <h1>WikiMeSH</h1>
      <hr />
      <h4>Outil de recherche des entrées wikipédia correspondant aux concepts MeSH</h4>
    </div>
    <div class="container" style="margin-top: 2rem;">
      <div id="navigation-links" class="row">
        <div class="col-md-4">
          <router-link class="btn btn-secondary navlink" to="/explorer">Explorer&nbsp;»</router-link>
          <!-- <a class="btn btn-secondary" href="/explorer" role="button">Explorer&nbsp;»</a> -->
        </div>
        <div class="col-md-4">
          <router-link class="btn btn-secondary navlink" to="/methodology">Méthodologie&nbsp;»</router-link>
        </div>
        <div class="col-md-4">
          <router-link class="btn btn-secondary navlink" to="/statistics">Statistiques&nbsp;»</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";

@Component
export default class Home extends Vue {
}
</script>

<style scoped>
body {
  background: #f7f7f7 !important;
}
.nav-tabs .nav-link.active {
  background: #f9f9f9;
}
.btn.btn-outline-primary {
  border: 1px solid #501450 !important;
  color: #501450 !important;
}

.btn.btn-outline-primary:hover {
  background: rgb(244, 225, 250) !important;
}
span.id{
  padding: 0.375rem 0rem;
  margin: 0 0.5rem;
  background: #ccf;
  font-size: 0.875rem;
  text-align: center;
  align: middle;
}
.loading{
  color: #aaa;
}
.wikilink{
  color: red;
}

#navigation-links{
  display: flex;
  align-items: center;
  justify-content: space-around;
  /* gap: 2rem; */
}

#navigation-links a.navlink{
  color: #fff;
  font-weight: bold;
  font-size: 1.375rem;
  padding: 2rem 1rem;
  margin-top: 1rem;
  width: 100%;
}

.jumbotron {
  padding: 2rem 1rem;
}
</style>
