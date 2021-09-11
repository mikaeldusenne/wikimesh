<template>
  <div class="container-fluid">
    <b-row class="justify-content-md-center">
      <b-col class="col-md-6">
        <h1>Statistiques</h1>
        <p>
          Statistiques descriptives des entrées wikipédia trouvées. 
        </p>
      </b-col>
    </b-row>
    
    <b-row class="justify-content-md-center">
      <b-col sm="12" md="10" lg="8" xl="6" v-if="stats">
        <p>
        Parmi les termes MeSH recherchés, <span class="number" v-html="prettyN(stats.overall.zero)" /> / <span class="number" v-html="prettyN(stats.overall.n)" /> (<span class="number" v-html="prettyN((stats.overall.zero_frac*100).toFixed(2)) + '%'" />) n'avaient pas de correspondance ou de traduction sur wikipédia.
        </p>
        <p>
        En moyenne on retrouvait <span class="number" v-html="prettyN(stats.overall.mean.toFixed(0))" /> (DS = <span class="number" v-html="prettyN(stats.overall.sd.toFixed(0))" />) traductions par concept MeSH trouvé.
        </p>
        <p>
          Les langues les plus fréquentes sont: <span class="number" v-for="e in top10lang">{{e}}</span>
        </p>
      </b-col>
    </b-row>

    <b-row class="justify-content-md-center">
      <b-col sm="12" md="10" lg="8" xl="6" v-if="stats">
        <div class="plot">
          <Barplot
            title="Répartition du nombre de traductions"
            xtitle="Nombre de traductions"
            ytitle="Nombre de termes MeSH"
            :xdata="stats.n_trads.map(e => e[0].toFixed(0))"
            :ydata="stats.n_trads.map(e => e[1])"
          />
        </div>
        <div class="plot">
          <Barplot
            title="Répartition du nombre d'entrées wikipedia par langue"
            xtitle="langue"
            ytitle="Nombre de d'entrées wikipedia"
            :xdata="stats.langs.map(e => e[0])"
            :ydata="stats.langs.map(e => e[1])"
          />
        </div>
      </b-col>
    </b-row>

  </div>
</template>

<script lang="ts">
import { Component, Vue, Watch } from "vue-property-decorator";
import axios from "axios";
import _ from 'lodash';
import Barplot from "@/components/Barplot.vue";
import { langCodes } from "@/langCodes.js";


@Component({
  components: {
    Barplot,
  }
})
export default class Stats extends Vue {
  stats: any = null;
  
  font: any = {
    family: 'Source Code Pro',
    color: "#000",
  }


  get top10lang(){
    return this.stats.langs.slice(0, 10).map(e => e[0] ).map(e => langCodes.find(ee => ee.code==e).name)
  }
  prettyN(n) {
    return n.toString().replace(/\B(?=(\d{3})+(?!\d))/g, "&nbsp;");
  }
  
  fetchData(){
    axios
    .get("/api/mesh-stats")
    .then(ans => {
      console.log('stats');
      console.log(ans.data);
      this.stats = ans.data
    })
    .catch(console.log);
  }
  mounted() {
    this.fetchData();
  }
}
</script>

<style scoped>
.row{
  margin-bottom: 2rem;
}

span.number{
  font-family: monospace;
  background-color: #ddd !important;
  padding: 0.175rem 0.375rem;
  font-size: 0.9rem;
  margin: 0 0.1rem;
  border-radius: 0.175rem;
  display: inline-block;
}
div.plot{
  margin-bottom: 2rem;
}
</style>
