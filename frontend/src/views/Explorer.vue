<template>
  <div class="container-fluid" id="explorer">
    <b-row class="justify-content-md-center">
      <b-col class="col-md-6" id="explorer-intro">
        <h1>Explorer</h1>
        <p>
          Here you can explore the Wikipedia links found for MeSH concepts.
        </p>
        <p>
          The pills <span class="pill pill-syn-pt">PT</span> ans <span class="pill pill-syn-pt">SYN</span>
          indicate wether Wikipedia links were identified thanks to a MeSH preferred term or a synonym.
        </p>
      </b-col>
    </b-row>
    
    <div class="row justify-content-md-center" style="margin: 1rem;" @keyup.enter="searchData" v-on:submit.prevent>
      <b-col sm="12" md="8" lg="6" xl="6" >
        <div class="container-fluid form">
          <transition-group name="list-form" tag="form">

            <div key="A" class="row-mb-2 form-check list-item-form">
              <div class="input-group" style="padding: 0.5rem 0.375rem;">
                <label>
                  <input type="checkbox" class="form-check-input"  v-model="filterOnlyNonEmpty" />
                  Hide empty entries
                </label>
              </div>
            </div>
            
            <div key="B" class="row mb-2 list-item-form">
              <div class="input-group">
                <input
                  id="searchform"
                  type="text"
                  maxlength="75"
                  class="form-control"
                  placeholder="search by term or MeSH ID"
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
            </div>
            
            <div key="CAA"
                 class="row mb-2 list-item-form" data-toggle="tooltip" data-placement="top" title="Language of the concept that allowed to find the Wikipedia entries">
              <label for="lang-match-search" class="col-sm-2 col-form-label">Identifier&nbsp;:</label>
              <div class="col-sm-10">
                <b-form-select
                  v-model="identifier"
                  :options="identifierOptions"
                  @change="searchData"
                  class="form-control form-control"
                />
              </div>
            </div>
            
            <div key="C" v-if="showAdvancedSearch"
                 class="row mb-2 list-item-form" data-toggle="tooltip" data-placement="top" title="Language of the concept that allowed to find the Wikipedia entries">
              <hr>
              <div><strong>Match type:</strong></div>
              <label for="lang-match-search" class="col-sm-2 col-form-label">Language&nbsp;:</label>
              <div class="col-sm-10">
                <b-form-select
                  id="lang-match-search"
                  v-model="langMatchSearch"
                  :options="langMatchOptions"
                  @change="searchData"
                  class="form-control form-control"
                />
              </div>
            </div>
            
            <div key="D" v-if="showAdvancedSearch"
                 class="row mb-2 list-item-form" data-toggle="tooltip" data-placement="top" title="Filtrer les match par PT / SYN">
              <label for="ptsyn-match-search" class="col-sm-2 col-form-label">Type&nbsp;:</label>
              <div class="col-sm-10">
                <b-form-select
                  id="ptsyn-match-search"
                  v-model="ptsynMatchSearch"
                  :options="ptsynMatchOptions"
                  @change="searchData"
                  class="form-control form-control"
                />
              </div>
            </div>
            
            
            <div key="CA" v-if="showAdvancedSearch"
                 class="row mb-2 list-item-form" data-toggle="tooltip" data-placement="top" title="">
              <hr>
              <div>
                <strong>Filter results:</strong>
                <!-- <p><em>Filter the results</em></p> -->
              </div>
              <label for="lang-match-search" class="col-sm-4 col-form-label">Language:</label>
              <div class="col-sm-8">
                <b-form-select
                  v-model="langSearch"
                  :options="langMatchOptions"
                  @change="searchData"
                  class="form-control form-control"
                />
              </div>
            </div>
            <!-- <div key="CB" v-if="showAdvancedSearch" class="row mb-2 list-item-form">
                 <label for="lang-match-search" class="col-sm-4 col-form-label">MeSH:</label>
                 <div class="col-sm-8" style="display: inline-grid; grid-template-columns: 33% 33% 33%">
                 <div class="form-check" style="display: inline;" v-for="yna in ['yes', 'no', 'all']">
                 <input class="form-check-input" @change="searchData"
                 :id="'langmesh-'+yna" type="radio" name="langMesh" :value="yna" v-model="langMesh">
                 <label class="form-check-label" :for="'langmesh-'+yna" >{{yna}}</label>
                 </div>
                 </div>
                 </div> -->
            <div key="CD" v-if="showAdvancedSearch" class="row mb-2 list-item-form">
              <label for="lang-match-search" class="col-sm-4 col-form-label">Wikipedia:</label>
              <div class="col-sm-8" style="display: inline-grid; grid-template-columns: 33% 33% 33%">
                <div class="form-check form-check-inline" v-for="yna in ['yes', 'no', 'all']">
                  <input class="form-check-input" @change="searchData"
                         :id="'langwiki-'+yna" type="radio" name="langWiki" :value="yna" v-model="langWiki">
                  <label class="form-check-label" :for="'langwiki-'+yna" >{{yna}}</label>
                </div>
              </div>
            </div>
            <!-- <div key="CC" v-if="showAdvancedSearch && langMesh!='no' && langWiki!='no'" class="row mb-2 list-item-form">
                 <label for="lang-match-search" class="col-sm-4 col-form-label">MeSH/Wiki match:</label>
                 <div class="col-sm-8" style="display: inline-grid; grid-template-columns: 25% 25% 25% 25%">
                 <div class="form-check form-check-inline" v-for="yna in ['pt', 'syn', 'none', 'all']">
                 <input class="form-check-input" @change="searchData"
                 :id="'langmeshtype-'+yna" type="radio"
                 name="langMeshType" :value="yna" v-model="langMeshType">
                 <label class="form-check-label" :for="'langmeshtype-'+yna" >{{yna}}</label>
                 </div>
                 </div>
                 </div> -->
            
              
            <hr key="Z" v-if="showAdvancedSearch"/>
            <div key="E" v-if="showAdvancedSearch"
                 class="row mb-2 list-item-form" data-toggle="tooltip" data-placement="top" title="Limiter la isualisation des liens à certaines langues">
              <label for="langview" class="col-sm-3 col-form-label">View&nbsp;:</label>
              <div class="col-sm-9">
                <b-form-select
                  id="langview"
                  v-model="langView"
                  :options="langViewOptions"
                  class="form-control form-control"
                />
              </div>
            </div>

            <div key="F" class="list-item-form" style="margin-top: 1rem;">
              <em v-if="!fetching">{{nMesh}} document{{nMesh>1?'s':''}}.</em>
              <em v-else>recherche...</em>
              <div style="float: right;">
                <em style="color: #555; text-decoration: underline; cursor: pointer;"
                    @click="toggleAdvancedSearch">
                  {{showAdvancedSearch?"normal search":"advanced search"}}
                </em>
              </div>
            </div>
            
            
          </transition-group>

        </div>
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
              <span><em style="font-size:0.9rem; color: #ddd;">{{m.wikilangs.langs.length}}&nbsp;languages.</em></span>
            </div>
            <span class="show-details" @click="toggleDetails(m)" style="position: absolute; right: 1rem;" data-toggle="tooltip" data-placement="top" :title="(m.showDetails?'hide':'show') + ' MeSH concept details'"><font-awesome-icon :icon="m.showDetails?'eye-slash':'eye'" /></span>
          </b-card-title>
          
          <b-card-body class="item-card-body">
            <b-container class="container-item">
              <!-- <b-row>
              -->
              <transition-group name="list" tag="div" class="row row-item">
                
                <b-col key="colMesh" class="conceptdetails list-item" lg="6" v-if="m.showDetails" style="margin-bottom: 1rem; max-height: 15rem; height: 15rem; overflow: auto;">
                    <p style="margin-bottom: 0.5rem;"><strong style="width: 100%;">Concept details:</strong></p>
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
                        <li v-for="[lang, l] in filterWiki(m.wikilangs.langs)" :class="{match: m.wikilangs.lang_match == lang}">
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
  showAdvancedSearch = false;
  langMatchSearch: string | null = null;
  ptsynMatchSearch: string | null = null;
  langView = null;
  
  languages: any[] = [];
  
  langSearch = null
  langMesh = "all"
  langMeshType = "all"
  langWiki = "all"

  identifier: null | string = null;
  identifiers: string[] = [];
  
  get identifierOptions(){
    const everything: any[] = [{text: "everything", value: null}];
    return everything.concat(this.identifiers.map(e => {
      return {
        text: e,
        value: e
      }
    }))
  }
  
  get langMatchOptions(){
    return [
      {text: "all languages", value: null},
      {text: "all except english", value: "no-english"},
    ].concat(_.sortBy(
      this.languages.map(e => {
        return {
          text: this.langFromCode(e),
          value: e,
        }
      }),
      [e => e.text.toLowerCase()]
    ))
  }
  
  
  get langViewOptions(){
    return [
      {text: "all languages", value: null},
      {text: "all languages except english", value: "no-english"},
    ].concat(_.sortBy(
      this.languages.map(e => {
        return {
          text: this.langFromCode(e),
          value: e,
        }
      }),
      [e => e.text.toLowerCase()]
    ))
  }
  
  filterWiki(langs){
    if(this.langView == null){
      return langs;
    }else{
      return langs.filter(([lang, l]) => (this.langView == "no-english" && lang != "en") || (lang == this.langView))
    }
  }
  
  ptsynMatchOptions = [
    {
      text: "PT + SYN",
      value: null
    }, {
      text: "PT",
      value: "pt"
    }, {
      text: "SYN",
      value: "syn"
    }
  ]

  mesh: Array<Mesh> = [];
  search = "";
  
  toggleAdvancedSearch(){
    this.showAdvancedSearch = !this.showAdvancedSearch;
    localStorage.setItem("showAdvancedSearch",JSON.stringify(this.showAdvancedSearch))
    if(!this.showAdvancedSearch){
      this.ptsynMatchSearch = null;
      this.langMatchSearch = null;
      this.langView = null;
    }
  }
  
  toggleDetails(m){
    m.showDetails=!m.showDetails
    // console.log(m.showDetails)
  }
  
  @Watch('ptsynMatchSearch')
  ptsynchgd(v){
    localStorage.setItem('ptsynMatchSearch', JSON.stringify(this.ptsynMatchSearch))
  }
  
  @Watch('langMatchSearch')
  langchgd(v){
    localStorage.setItem('langMatchSearch', JSON.stringify(this.langMatchSearch))
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
    return (lang&&lang.name)?lang.name:c;
  }

  searchData(){
    // this.currentPage = 1;
    if(this.$route.query.search != this.search){
      this.$router.replace({path: this.$route.path, query: {...this.$route.query, ...{search: this.search}}}).catch(console.log)
    }
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
      langMatchSearch: this.langMatchSearch,
      ptsynMatchSearch: this.ptsynMatchSearch,
      filterOnlyNonEmpty: this.filterOnlyNonEmpty,
      langSearch: this.langSearch,
      langMesh: this.langMesh,
      langMeshType: this.langMeshType,
      langWiki: this.langWiki,
      identifier: this.identifier,
    }})
    .then(ans => {
      console.log('MESH fetched')
      console.log(ans.data)
      this.nMesh = ans.data.count
      this.fetching = false;
      this.mesh = ans.data.data.map(e => {
        e.showDetails = true;
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

  fetchLanguages(){
    axios.get('api/languages').then(e => {
      this.languages = e.data;
      console.log('LANGUAGES:')
      console.log(this.languages)
    }).catch(console.log)
  }
  
  fetchIdentifiers(){
    axios.get('api/identifiers').then(e => {
      this.identifiers = e.data;
      console.log(this.identifiers)
    }).catch(console.log)
  }
  
  tryParseLocalStorage(name){
    const localval = localStorage.getItem(name);
    if(localval){
      try {
        const ans = JSON.parse(localval)
        console.log('LOCALSTORAGE SEARCHED ' + name)
        console.log(ans)
        return ans
      } catch (error) {
        console.error(error);
        console.log('error localstorage decode '+name+' :')
        console.log(localval)
      }
    }
  }
  
  
  mounted() {
    this.search = (this.$route.query.search as string) || "";

    this.showAdvancedSearch = this.tryParseLocalStorage("showAdvancedSearch") || this.showAdvancedSearch
    this.ptsynMatchSearch = this.tryParseLocalStorage("ptsynMatchSearch") || this.ptsynMatchSearch
    this.langMatchSearch = this.tryParseLocalStorage("langMatchSearch") || this.langMatchSearch
    
    console.log(this.$route)
    this.fetchData();
    this.fetchLanguages();
    this.fetchIdentifiers();
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

a{
  color: #222;
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

/*  ----------------  */

.list-item-form {
  transition: all .25s;
}

.list-form-enter, .list-form-leave-to{
  opacity: 0;
  transform: translateY(-30px);
}

.list-form-leave-active {
  position: absolute;
}

/*  ----------------  */

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

li.match a{
  font-weight: 800;
}

.form{
  background-color: #eee;
  border: 1px solid #aaa;
  padding: 1rem;
  border-radius: 0.5rem;
}
</style>
