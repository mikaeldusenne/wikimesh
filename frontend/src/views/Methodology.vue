<template>
  <div class="container-fluid">
    <b-row class="justify-content-md-center">
      <b-col class="col-md-6">
        <h1>Méthodologie</h1>
      </b-col>
    </b-row>
    <b-row class="d-flex justify-content-center">
      <b-col xs="12" sm="8" xl="6">
        <p>
          Le but de cet outil est de retrouver les entrées wikipédia en différentes langues pour les termes du thésaurus <a href="https://www.hetop.eu/hetop/rep/uk/MESH/" target="_blank">MeSH</a>.
        </p>
        <p>
          L'<a href="https://www.mediawiki.org/wiki/API:Main_page" target="_blank">API wikipédia</a> permet de rechercher les <a href="https://www.mediawiki.org/wiki/API:Langlinks" target="_blank">liens linguistiques</a> pour une page donnée, permettant d'explorer en différentes langues les pages d'un sujet donné.
        </p>
        <p>
          Pour chaque terme MeSH, une recherche de l'entrée correspondante sur wikipedia a été réalisée.<br>
          Afin de maximiser le rappel, utilisé l'algorithme suivant:<br>
          <ul style="margin-top: 1rem; max-width: 80%;">
            <li>
              Si une entrée wikipédia était retrouvée pour le <a href="https://www.nlm.nih.gov/mesh/concept_structure.html" target="_blank">terme préféré</a> en anglais du concept recherché, les liens linguistiques de cette page étaient retournés. 
            </li>
            <li>
              Sinon, ne recherche utilisant les synonymes du terme MeSH était utilisée. Si l'un des synonymes permettait de retrouver une page wikipédia, les liens associés à cette page étaient retournés.
            </li>
            <li>
              Si nécessaire, les étapes ci-dessus étaient répétées pour les autres langues disponibles pour le concept MeSH. La recherche s'arrête dès qu'une page a été retrouvée.
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
