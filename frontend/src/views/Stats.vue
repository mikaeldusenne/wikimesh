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
        <hr>
        <p>
          <span class="number" v-html="prettyN(stats.en.overall.n)" /> Documents ont été retrouvés grâve à un terme MeSH en anglais (<span class="number" v-html="prettyN(stats.en.overall.mean.toFixed(0))" /> &#177; <span class="number" v-html="prettyN(stats.en.overall.sd.toFixed(0))" /> traductions par terme MeSH),<br>
        </p><p>
          <span class="number" v-html="prettyN(stats.not_en.overall.n)" /> Documents ont été retrouvés grâve à un terme MeSH dans une autre langue que l'anglais (l'anglais n'ayant pas retourné de résultat) (<span class="number" v-html="prettyN(stats.not_en.overall.mean.toFixed(0))" /> &#177; <span class="number" v-html="prettyN(stats.not_en.overall.sd.toFixed(0))" /> traductions par terme MeSH)<br>
        </p>
          <div style="display: flex; justify-content: center;">
            
            <table class="table table-sm table-bordered table-hover" style="font-family: monospace; width: auto !important;">
              <caption>Table de contingence des termes ayant permis de retrouver les pages Wikipédia</caption>
              <thead>
                <tr>
                  <th class="title" scope="col"></th>
                  <th class="title" scope="col">Anglais</th>
                  <th class="title" scope="col">Autre</th>
                  <th class="title" scope="col"></th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <th class="title" scope="row">Terme préféré</th>
                  <td class='number'             v-html="prettyN(stats.contingency.find(([[ka, kb], e]) => (ka=='pt' && kb=='en'))[1])"></td>
                  <td class='number'             v-html="prettyN(stats.contingency.find(([[ka, kb], e]) => (ka=='pt' && kb=='not_en'))[1])"></td>
                  <th class='number' scope='row' v-html="prettyN(sum(stats.contingency.filter(([[ka, kb], e]) => (ka=='pt')).map(e => e[1])))"></th>
                </tr>
                <tr>
                  <th class="title" scope="row">Synonyme</th>
                  <td class="number"             v-html="prettyN(stats.contingency.find(([[ka, kb], e]) => (ka=='syn' && kb=='en'))[1])"></td>
                  <td class="number"             v-html="prettyN(stats.contingency.find(([[ka, kb], e]) => (ka=='syn' && kb=='not_en'))[1])"></td>
                  <th class="number" scope="row" v-html="prettyN(sum(stats.contingency.filter(([[ka, kb], e]) => (ka=='syn')).map(e => e[1])))"></th>
                </tr>
                <tr>
                  <th class="title" scope="row"></th>
                  <th class='number' scope='row' v-html="prettyN(sum(stats.contingency.filter(([[ka, kb], e]) => (kb=='en')).map(e => e[1])))"></th>
                  <th class='number' scope='row' v-html="prettyN(sum(stats.contingency.filter(([[ka, kb], e]) => (kb=='not_en')).map(e => e[1])))"></th>
                  <th class='number' scope='row' v-html="prettyN(sum(stats.contingency.map(e => e[1])))"></th>
                </tr>
              </tbody>
            </table>
          </div>
      </b-col>
    </b-row>

    <div class="row justify-content-md-center" style="margin: 1rem;" @keyup.enter="searchData" v-on:submit.prevent>
      <b-col sm="12" md="8" lg="6" xl="4" >
        <div class="container-fluid form">
          <form>
            <div class="row mb-2 list-item-form">
              <label for="selecttdata" class="col-sm-3 col-form-label">Données&nbsp;:</label>
              <div class="col-sm-9">
                <b-form-select
                  id="selecttdata"
                  v-model="plotData"
                  :options="plotDataOptions"
                  class="form-control"
                />
              </div>
            </div>
          </form>
        </div>
      </b-col>
    </div>
            
    <b-row class="justify-content-md-center">
      <b-col sm="12" md="10" lg="8" xl="6" v-if="stats">
        <div class="plot">
          <Barplot
            title="Répartition du nombre de traductions"
            xtitle="Nombre de traductions"
            ytitle="Nombre de termes MeSH"
            :xdata="statsplotdata.n_trads.map(e => e[0].toFixed(0))"
            :ydata="statsplotdata.n_trads.map(e => e[1])"
          />
        </div>
        <!-- </b-col>
             <b-col sm="12" md="10" lg="8" xl="6" v-if="stats"> -->
        <div class="plot">
          <Barplot
            title="Répartition du nombre d'entrées wikipedia par langue"
            xtitle="langue"
            ytitle="Nombre de d'entrées wikipedia"
            :xdata="statsplotdata.langs.map(e => e[0])"
            :ydata="statsplotdata.langs.map(e => e[1])"
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
import Boxplot from "@/components/Boxplot.vue";
import { langCodes } from "@/langCodes.js";


@Component({
  components: {
    Barplot,
    Boxplot
  }
})
export default class Stats extends Vue {
  stats: any = null;
  plotData: string | null = null;
  
  plotDataOptions = [
    {
      text: "Tout",
      value: null
    },
    {
      text: "Anglais",
      value: "en"
    },
    {
      text: "Tout sauf Anglais",
      value: "not_en"
    },
    {
      text: "Terme préféré",
      value: "pt"
    },
    {
      text: "Synonyme",
      value: "syn"
    },
  ]

  get statsplotdata(){
    return this.plotData == null ? this.stats : this.stats[this.plotData];
  }
  
  font: any = {
    family: 'Source Code Pro',
    color: "#000",
  }
  
  sum(l){
    return !l?0:l.length==1?l[0]:l.reduce((a, b) => a+b)
  }
  
  get top10lang(){
    return this.stats.langs.slice(0, 10).map(e => e[0] ).map(e => {
      const code = langCodes.find(ee => ee.code==e)
      return code?code.name:e
    })
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

th.number, td.number{
  text-align: right;
  padding: 0.75rem;
}

th.title, td.title{
  text-align: right;
  padding: 0.75rem;
}


</style>
