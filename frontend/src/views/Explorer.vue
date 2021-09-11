<template>
  <div class="container-fluid" id="explorer">
    <b-row class="justify-content-md-center">
      <b-col class="col-md-6">
        <h1>Explorer</h1>
        <p>
          Cette section permet d'explorer les liens wikipédia retrouvés pour les concepts MeSH.
        </p>
      </b-col>
    </b-row>

    <div class="row justify-content-md-center" style="margin: 1rem 0 2rem 0;" @keyup.enter="searchData">
      <b-col sm="12" md="8" lg="6" xl="4">
        <div class="form-check">
          <label for="inputhideempty">
            <input id="inputhideempty" type="checkbox" class="form-check-input"  v-model="filterOnlyNonEmpty" />
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
        
        <em v-if="!fetching">{{nMesh}} documents.</em>
        <em v-else>recherche...</em>
      </b-col>
    </div>

    
    <b-row v-if="!error" class="justify-content-md-center" :class="{fetching: fetching}">
      <b-col sm="12" md="8" lg="6" xl="4">
        <b-card v-for="m in mesh" :key="m.id">
          <b-card-title style="display: flex; align-items: center;" class="item-title">
            <div class="id">{{m._id}}</div>
            <div class="meshterm">
              {{m.langs[0].pt}}
              <span><em style="font-size:0.9rem; color: #ddd;">{{Object.keys(m.wikilangs.langs || {}).length}}&nbsp;langues.</em></span>
            </div>
          </b-card-title>
          <b-card-body v-if="Object.keys(m.wikilangs.langs || {}).length" style="max-height: 15rem; overflow: auto;">
            <div class="langlinks">
              <ul>
                <li v-for="l, lang in m.wikilangs.langs">
                  <a class="wikilink" target="_blank" :href="'https://'+lang+'.wikipedia.org/wiki/'+l">[{{langFromCode(lang)}}] {{l}}</a>
                </li>
              </ul>
            </div>
          </b-card-body>
          <b-card-body v-else>
            <div class="langlinks" style="margin-top: 1rem;">
              <ul><li>Entrée wikipédia non trouvée </li></ul>
            </div>
          </b-card-body>
        </b-card>
      </b-col>
    </b-row>
    <!-- <b-row v-else-if="fetching" class="justify-content-md-center">
         <b-col sm="12" md="8" lg="6" xl="4">
         <div class="alert alert-secondary">Recherche...</div>
         </b-col>
         </b-row> -->
    <b-row v-else-if="error" class="justify-content-md-center">
      <b-col sm="12" md="10" lg="8" xl="6">
        <div class="alert alert-danger" v-html="error"></div>
      </b-col>
    </b-row>

    <b-row style="position: sticky; bottom: 0; z-index: 9000;">
      <b-pagination
        class="pagination"
        style="display: flex; justify-content: center;"
        v-model="currentPage"
        :total-rows="nMesh"
        :per-page="perPage"
      ></b-pagination>
    </b-row>

  </div>
</template>

<script lang="ts">
import { Component, Vue, Watch } from "vue-property-decorator";
import axios from "axios";
import { langCodes } from "@/langCodes.js";

axios.defaults.baseURL = process.env.BASE_URL;

interface Mesh{
  id: string;
  title: string;
  links: string[];
}

@Component
export default class Explorer extends Vue {
  nMesh = 0;
  perPage = 10;
  currentPage = 1;
  filterOnlyNonEmpty = true;
  error = null;
  fetching = false;
  
  mesh: Array<Mesh> = [];
  search = "";

  @Watch('currentPage')
  cpchgd(v, oldv){
    console.log(`current page changed ${oldv} -> ${v}`)
    this.fetchData();
  }
  
  @Watch('filterOnlyNonEmpty')
  oechgd(v){
    console.log('filter only nonempty changed')
    this.currentPage = 1;
    this.fetchData();
  }

  langFromCode(c){
    // console.log("LANGCODES")
    // console.log(langCodes)
    let lang = langCodes.find(e => e.code == c);
    return lang?lang.name:c;
  }

  searchData(){
    // this.currentPage = 1;
    this.fetchData();
  }
  
  fetchData(){
    // this.mesh=[];
    this.fetching = true;
    this.error = null;
    const page = this.currentPage;
    console.log('CURRENTPAGE ' + page)
    axios
    .get("/api/mesh", {params: {
      from: (page-1) * this.perPage,
      limit: this.perPage,
      search: this.search || null,
      filterOnlyNonEmpty: this.filterOnlyNonEmpty,
    }})
    .then(ans => {
      console.log('MESH fetched')
      // console.log(ans.data)
      this.nMesh = ans.data.count
      this.fetching = false;
      this.mesh = ans.data.data
    })
    .catch(err => {
      console.log(err);
      this.fetching = false;
      this.error=err.response.data;
    });
  }
  mounted() {
    this.fetchData();
  }
}
</script>

<style scoped>
body {
  background: #f7f7f7 !important;
}
.nav-tabs .nav-link.active {
  background: #f9f9f9;
}

.btn.btn-outline-primary:hover {
  background: rgb(244, 225, 250) !important;
}
.meshterm{
  margin: 0.5rem;
}
.id{
  padding: 0.375rem 0.5rem;
  border-radius: 0.2rem;
  margin: 0.5rem;
  background: #ccc;
  color: #222;
  font-size: 0.875rem;
  text-align: center;
  align: middle;
}
.loading{
  color: #aaa;
}
#explorer a.wikilink{
  color: #222;
}
div.langlinks{
  display: flex;
  justify-content: left;
}
ul {
  list-style-type: none;
}
.card-body{
  padding: 0;
}
.card{
  margin-bottom: 1rem;
}
.item-title{
  background: #666;
  color: #fff;
  padding: 1rem;
  border-radius: 0.25rem;
  flex-wrap: wrap;
}

.fetching{
  opacity: 0.5 !important;
}

</style>
