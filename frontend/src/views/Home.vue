<template>
  <div class="container">
    <b-row class="justify-content-md-center">
      <b-col class="col-md-12">
        <div class="alert text-light bg-dark">
          <h1>Traducteur MeSH</h1>
        </div>
          <h5>Cet outil recherche des traductions de concepts MeSH via les liens linguistiques de wikipédia.</h5>
      </b-col>
    </b-row>

    <div class="row justify-content-md-center" style="margin: 1rem 0;" @keyup.enter="searchData">
      <b-col sm="11" md="10" lg="8" xl="6">
        <div class="form-check">
          <input type="checkbox" class="form-check-input"  v-model="filterOnlyNonEmpty" />
          <label>
            Masquer les entrées vides
          </label>
        </div>
        
        <div class="input-group">
          <input
            type="text"
            maxlength="30"
            class="form-control"
            placeholder="recherche en anglais / ID MeSH"
            v-model="search"
          />
          <div class="input-group-append">
            <button
              @click="searchData"
              class="btn btn-outline-secondary"
              type="button"
            >
              rechercher
            </button>
          </div>
        </div>
        

      </b-col>
    </div>

    <b-row style="position: sticky; top: 0; z-index: 9000;">
      <b-pagination
        class="pagination"
        style="display: flex; justify-content: center;"
        v-model="currentPage"
        :total-rows="nMesh"
        :per-page="perPage"
      ></b-pagination>
    </b-row>
    
    <b-row class="justify-content-md-center">
      <b-col sm="11" md="10" lg="8" xl="6">
        <b-card v-for="m in mesh" :key="m.id">
          <b-card-title style="display: grid; grid-template-columns: 30% 70%; align-items: center;">
            <span class="id">{{m._id}}</span>
            <span>{{m.title}}</span>
          </b-card-title>
          <b-card-body>
            <ul v-if="Object.keys(m.links).length" style="max-height: 8rem; overflow: auto;">
              <li v-for="l, lang in m.links">
                <a class="wikilink" target="_blank" :href="'https://'+lang+'.wikipedia.org/wiki/'+l">({{lang}}) {{l}}</a>
              </li>
            </ul>
            <div v-else>
              Entrée wikipédia non trouvée 
            </div>
          </b-card-body>
        </b-card>
      </b-col>
    </b-row>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Watch } from "vue-property-decorator";
import axios from "axios";

axios.defaults.baseURL = process.env.BASE_URL;

interface Mesh{
  id: string;
  title: string;
  links: string[];
}

@Component
export default class Home extends Vue {
  nMesh = 0;
  perPage = 10;
  currentPage = 1;
  filterOnlyNonEmpty = true;
  
  mesh: Array<Mesh> = [];
  search = "";

  @Watch('currentPage')
  cpchgd(v){
    this.fetchData(v);
  }
  
  @Watch('filterOnlyNonEmpty')
  oechgd(v){
    this.fetchData(v);
  }

  searchData(){
    this.currentPage = 0;
    this.fetchData(1);
  }
  
  fetchData(page){
    axios
    .get("/api/mesh", {params: {
      from: (page-1) * this.perPage,
      limit: this.perPage,
      search: this.search || null,
      filterOnlyNonEmpty: this.filterOnlyNonEmpty,
    }})
    .then(ans => {
      console.log('MESH')
      console.log(ans.data)
      this.nMesh = ans.data.count
      this.mesh = ans.data.data
    })
    .catch(console.log);
  }
  mounted() {
    this.fetchData(1);
  }
}
</script>

<style>
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
</style>
