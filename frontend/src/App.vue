<template>
  <div id="app">
    <NavBar />
    <div id="content">
      <router-view />
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";

import NavBar from "@/components/NavBar.vue";

@Component({
  components: {
    NavBar
  }
})
export default class App extends Vue {}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

#content {
  margin-top: 2rem;
}

#content a.router-link-exact-active {
  color: #42b983;
}

.pagination{
  margin-bottom: 0rem !important;
}

.pagination .page-link{
  color: #eee !important;
}


.pagination .page-item.active .page-link{
  background-color: #666 !important;
  border-color: #666 !important;
  box-shadow: none !important;
}

.pagination .page-item .page-link{
  background-color: #444 !important;
  border-color: #444 !important;
  box-shadow: none !important;
}
</style>
