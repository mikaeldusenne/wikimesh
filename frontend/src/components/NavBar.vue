<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    
    <a class="navbar-brand" href="/mesh-translator">
      <b-nav-item to="/">WikiMeSH</b-nav-item>
    </a>

    <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>

    <b-collapse id="nav-collapse" is-nav>
      <b-navbar-nav class="ml-auto">
        <b-nav-item to="/explorer">Explorer</b-nav-item>
        <b-nav-item to="/methodology">Méthodologie</b-nav-item>
        <b-nav-item to="/statistics">Statistiques</b-nav-item>
      </b-navbar-nav>
    </b-collapse>
  </nav>
</template>

<script lang="ts">
import { Component, Prop, Vue } from "vue-property-decorator";
import { mapGetters } from 'vuex'

@Component({
  computed: mapGetters(['getId'])
})
export default class NavBar extends Vue {
  showLogin = false;
}
</script>

<style scoped>
 /* unvisited link */
a:link {
  color: white;
}

/* visited link */
a:visited {
  color: white;
}

/* mouse over link */
a:hover {
  color: white;
}

/* selected link */
a:active {
  color: white;
} 
</style>
