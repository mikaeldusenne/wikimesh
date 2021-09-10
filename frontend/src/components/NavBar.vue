<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    
    <a class="navbar-brand" href="/mesh-translator">
      <b-nav-item to="/">Traducteur Mesh</b-nav-item>
    </a>

    <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>

    <b-collapse id="nav-collapse" is-nav>
      <b-navbar-nav class="ml-auto">
        <b-nav-item to="/stats">Statistics</b-nav-item>
        <b-navbar-nav v-if="showLogin && !getId">
          <b-nav-item to="/login">Connexion</b-nav-item>
          <b-nav-item to="/register">Inscription</b-nav-item>
        </b-navbar-nav>
        <b-navbar-nav v-else-if="showLogin">
          <b-nav-item to="/profile">
            <font-awesome-icon icon="user" />
            {{ getId }}
          </b-nav-item>
          <b-nav-item to="#" v-if="getId" v-on:click="logout()" href="#">
            logout
          </b-nav-item>
          
          <b-nav-item-dropdown right>
            <!-- Using 'button-content' slot -->
            <template v-slot:button-content>
              <em>User</em>
            </template>
            <b-dropdown-item href="#">Profil</b-dropdown-item>
            <b-dropdown-item href="#">
              <b-nav-item to="#" v-if="getId" v-on:click="logout()" href="#">
                Déconnexion
              </b-nav-item>
            </b-dropdown-item>
          </b-nav-item-dropdown>
          <b-avatar text=""></b-avatar>
        </b-navbar-nav>

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
