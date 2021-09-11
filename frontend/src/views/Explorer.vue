<template>
  <div class="container-fluid" id="explorer">
    <b-row class="justify-content-md-center">
      <b-col class="col-md-6" id="explorer-intro">
        <h1>Explorer</h1>
        <p>
          Cette section permet d'explorer les liens wikipédia retrouvés pour les concepts MeSH.
        </p>
        <p>
          Survolez les concepts pour voir quel terme MeSH d'un concept a permis de retrouver les articles wikipédia.
        </p>
        <p>
          Les pilules <span class="pill pill-syn-pt">PT</span> et <span class="pill pill-syn-pt">SYN</span> indiquent si la page wikipédia a été trouvée grâce à un terme préféré MeSH ou à un synonyme.
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
      <b-col sm="12" md="10" lg="8" xl="6">
        <b-card v-for="m in mesh" :key="m.id">
          <b-card-title style="display: flex; align-items: center;" class="item-title">
            <div class="pill id">{{m._id}}</div>
            <div class="pill pill-syn-pt" v-if="m.wikilangs.origin">
              {{m.wikilangs.origin.toUpperCase()}}
            </div>
            <div class="meshterm" data-toggle="tooltip" data-placement="top" :title="matchInfo(m)">
              {{m.langs[0].pt}}
              <span><em style="font-size:0.9rem; color: #ddd;">{{m.wikilangs.langs.length}}&nbsp;langues.</em></span>
            </div>
            <span class="show-details" @click="toggleDetails(m)" style="position: absolute; right: 1rem;" data-toggle="tooltip" data-placement="top" :title="(m.showDetails?'masquer':'afficher') + ' les détails du concept MeSH'"><font-awesome-icon :icon="m.showDetails?'eye-slash':'eye'" /></span>
          </b-card-title>
          
          <b-card-body class="item-card-body">
            <b-container class="container-item">
              <!-- <b-row>
              -->
              <transition-group name="list" tag="div" class="row row-item">
                
                <b-col key="colMesh" class="conceptdetails list-item" lg="6" v-if="m.showDetails" style="margin-bottom: 1rem; max-height: 15rem; height: 15rem; overflow: auto;">
                    <p style="margin-bottom: 0.5rem;"><strong style="width: 100%;">Détails du concept:</strong></p>
                    <p><strong>id:&nbsp;</strong>{{m._id}}</p>
                    <div v-for="e in m.langs" :key="e._id">
                      <hr style="margin: 0.25rem;" />
                      <strong>{{langFromCode(e._id)}}:&nbsp;</strong> {{e.pt}}
                      <div v-if="e.syns.length">
                        <em>synonyms:&nbsp;</em>
                        <ul style="margin-bottom: 0;"><li v-for="s in e.syns">-&nbsp;{{s}}</li></ul>
                      </div>
                    </div>
                  </b-col>
                  
                  <b-col key="colWikipedia" lg="6" class="linksdetails list-item" v-if="m.wikilangs.langs.length" style="margin-bottom: 1rem; max-height: 15rem; height: 15rem; overflow: auto;">
                    <strong style="width: 100%;" v-if="m.showDetails">Liens:</strong>
                    <div style="display: block;">
                      <ul>
                        <li v-for="[lang, l] in m.wikilangs.langs">
                          <a class="wikilink" target="_blank" :href="'https://'+lang+'.wikipedia.org/wiki/'+l">[{{langFromCode(lang)}}] {{l}}</a>
                        </li>
                      </ul>
                    </div>
                  </b-col>
                  <b-col key="colWikipedia" class="list-item" v-else>
                    <div class="langlinks" style="margin-top: 1rem;">
                      <ul><li>Entrée wikipédia non trouvée </li></ul>
                    </div>
                  </b-col>
              </transition-group>

              <!-- </b-row>
              -->
            </b-container>
            
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
import _ from "lodash";

axios.defaults.baseURL = process.env.BASE_URL;

interface Mesh{
  id: string;
  title: string;
  links: string[];
  showDetails: boolean;
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
  
  toggleDetails(m){
    m.showDetails=!m.showDetails
    console.log(m.showDetails)
  }
  
  
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
  
  matchInfo(m){
    if(m.wikilangs){
      return `match: (${this.langFromCode(m.wikilangs.lang_match)}) ${m.wikilangs.term_match}`
    }
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
      console.log(ans.data)
      this.nMesh = ans.data.count
      this.fetching = false;
      this.mesh = ans.data.data.map(e => {
        e.showDetails = false;
        e.wikilangs.langs = _.sortBy(Object.entries(e.wikilangs.langs || {}), [
          ([k, v]) => this.langFromCode(k).toLowerCase()
        ])
        return e;
      })
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
  margin: 0.5rem 0.25rem;
}

.pill{
  padding: 0.375rem 0.5rem;
  border-radius: 0.2rem;
  margin: 0.5rem 0.25rem;
  font-size: 0.875rem;
  text-align: center;
  align: middle;
  color: #222;
}

.pill-syn-pt{
  background: #ada;
}

.id{
  background: #ccc;
}

.loading{
  color: #aaa;
}

#explorer a.wikilink{
  color: #222;
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
  margin-bottom: 0;
}

.fetching{
  opacity: 0.5 !important;
}

.show-details{
  font-size: 0.9rem;
  margin: 0.25rem;
  padding: 0.5rem;
  padding-top: 0.625rem;
  border: 1px solid #444;
  border-radius: 0.2rem;
  background-color: #444;
  color: #ddd;
  cursor: pointer;
}


#explorer-intro p{
  margin-bottom: 0;
}

#explorer-intro{
  margin-bottom: 1rem;
}

.list-item {
  display: inline-block;
  background: white;
  transition: all .5s;
}

.list-enter, .list-leave-to
/* .list-complete-leave-active below version 2.1.8 */ {
  opacity: 0;
  /* transform: translateY(-30px); */
}

.list-leave-active {
  position: absolute;
}

.conceptdetails{
  background-color: #ddd;
  padding: 1rem;
  margin: 0;
}

.linksdetails{
  padding: 1rem;
  margin: 0;
}

.conceptdetails p{
  margin-bottom: 0;
}

.row-item{
  margin: 0;
}

.container-item{
  padding: 0;
}
</style>
