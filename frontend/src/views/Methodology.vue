<template>
  <div class="container-fluid">
    <b-row class="justify-content-md-center">
      <b-col class="col-md-6">
        <h1>Methodology</h1>
      </b-col>
    </b-row>
    <b-row class="d-flex justify-content-center">
      <b-col xs="12" sm="8" xl="6">
        <p>
          The goal of this tool is to find wikipedia entries in different languages for the terms of the <a href="https://www.hetop.eu/hetop/rep/uk/MESH/" target="_blank">MeSH</a> thesaurus.
        </p>
        <p>
          The <a href="https://www.mediawiki.org/wiki/API:Main_page" target="_blank">Wikipedia API</a> allows to find the <a href="https://www.mediawiki.org/wiki/API:Langlinks" target="_blank">linguistic links</a> for a given page, allowing for the exploration of a given topic in different languages.
        </p>
        <p>
          For each MeSH term, a search for the corresponding entry on wikipedia was performed.<br>
          In order to maximize recall, the following algorithm was used:<br>
          <ul style="margin-top: 1rem; max-width: 80%;">
            <li>
              If a wikipedia entry was found for the <a href="https://www.nlm.nih.gov/mesh/concept_structure.html" target="_blank">preferred term</a> in english of the concept of interest, linguistic links of this page were used. 
            </li>
            <li>
              Otherwise, a search using the synonyms of the MeSH term was used. If one of the synonyms allowed to find a Wikipedia entry, the linguistic links associated to this page were used.
            </li>
            <li>
              If necessary, the abovementionned steps were repeated for the other available languages for the MeSH concept. The search stops as soon as a page was found.
            </li>
          </ul>
            
        </p>
        
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
export default class Methodology extends Vue {
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

<style scoped>
li{
  margin-bottom: 1rem;
}
</style>
