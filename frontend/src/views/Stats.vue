<template>
  <div class="container-fluid" v-if="stats">
    <b-row class="justify-content-md-center">
      <b-col class="col-md-6">
        <h1>Statistiques</h1>
        <p>
          Statistiques descriptives des entrées wikipédia trouvées. 
        </p>
        <div class="container-fluid form">
          <form>
            <div class="row mb-2 list-item-form">
              <label for="selecttdata" class="col-sm-2 col-form-label">Identifier&nbsp;:</label>
              <div class="col-sm-10">
                <b-form-select
                  v-model="identifier"
                  :options="identifierOptions"
                  class="form-control form-control"
                />
              </div>
            </div>
          </form>
        </div>
      </b-col>
    </b-row>
    <div>
      
      <div class="row justify-content-md-center" style="margin: 1rem;" @keyup.enter="searchData" v-on:submit.prevent>
        <b-col sm="12" md="8" lg="6" xl="6" >
          <div class="card">
            <div class="card-header">
              <div style="margin-bottom: 1rem;"><strong>{{identifier}} translations vs Wikipedia entries</strong></div>
              <div class="container-fluid form">
                <form>
                  <div class="row mb-2 list-item-form">
                    <label for="selecttdata" class="col-sm-2 col-form-label">See&nbsp;:</label>
                    <div class="col-sm-10">
                      <b-form-select
                        v-model="matchReportView"
                        :options="matchReportOptions"
                        class="form-control"
                      />
                    </div>
                  </div>
                </form>
              </div>
            </div>
            <div class="card-body">
              <p>
                
                <div v-if="matchReportView != 'overall'">
                  Among the {{identifier}} terms in <span class="number">{{langFromCode(matchReportView)}}</span>,
                </div>
                <div v-else>
                  Among all languages of all {{identifier}} terms,
                </div>
                <br>
                <span class="number" v-html="prettyN(stats.match_report[matchReportView].not_in_wiki || 0)" /> didn't have an associated wikipedia page, <br>
                <span class="number" v-html="prettyN(stats.match_report[matchReportView].not_in_mesh || 0)" /> had a wikipedia page but no {{identifier}} translation in this language,<br>
                <span class="number" v-html="prettyN(stats.match_report[matchReportView].no_match || 0)" /> had entries both in the {{identifier}} and in wikipedia, but nor the Preferred Term not the Synonyms corresponded to the wikipedia entry. <br>
                
                
              </p>
              <p>
                For <span class="number" v-html="prettyN(stats.match_report[matchReportView].pt || 0)" /> {{identifier}} terms, the Preferred Term matched the wikipedia entry.<br>
                For <span class="number" v-html="prettyN(stats.match_report[matchReportView].syn || 0)" /> {{identifier}} terms, one of the synonyms matched the wikipedia entry.
              </p>
              
            </div>
          </div>
        </b-col>
        
      </div>


      <!-- <pre>
           {{JSON.stringify(stats.match_report, null, 2)}}
           </pre> -->
    </div>
    <b-row class="justify-content-md-center">
      <b-col sm="12" md="10" lg="8" xl="6" v-if="stats">
        <p>
          Among the searched {{identifier}} terms, <span class="number" v-html="prettyN(stats.overall.zero)" /> / <span class="number" v-html="prettyN(stats.overall.n)" /> (<span class="number" v-html="prettyN((stats.overall.zero_frac*100).toFixed(2)) + '%'" />) did not have a corresponding entry on Wikipedia.
        </p>
        <p>
        On average there existed <span class="number" v-html="prettyN(stats.overall.mean.toFixed(0))" /> (DS = <span class="number" v-html="prettyN(stats.overall.sd.toFixed(0))" />) translations per concept found.
        </p>
        <p>
          The most frequent languages are: <span class="number" v-for="e in top10lang">{{e}}</span>
        </p>
        <hr>
        <p>
          <span class="number" v-html="prettyN(stats.en.overall.n)" /> Documents were found thanks to an english {{identifier}} term (<span class="number" v-html="prettyN(stats.en.overall.mean.toFixed(0))" /> &#177; <span class="number" v-html="prettyN(stats.en.overall.sd.toFixed(0))" /> translation per {{identifier}} term),<br>
        </p><p>
          <span class="number" v-html="prettyN(stats.not_en.overall.n)" /> Documents were found thanks to a {{identifier}} term in another language than english (in the event where the english term did not return any Wikipedia entry) (<span class="number" v-html="prettyN(stats.not_en.overall.mean.toFixed(0))" /> &#177; <span class="number" v-html="prettyN(stats.not_en.overall.sd.toFixed(0))" /> translation per {{identifier}} term)<br>
        </p>
          <div style="display: flex; justify-content: center;">
            
            <table class="table table-sm table-bordered table-hover" style="font-family: monospace; width: auto !important;">
              <caption>Contingency table of the way the Wikipedia pages were found</caption>
              <thead>
                <tr>
                  <th class="title" scope="col"></th>
                  <th class="title" scope="col">English</th>
                  <th class="title" scope="col">Other</th>
                  <th class="title" scope="col"></th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <th class="title" scope="row">Preferred Term</th>
                  <td class='number'             v-html="prettyN(stats.contingency.find(([[ka, kb], e]) => (ka=='pt' && kb=='en'))[1])"></td>
                  <td class='number'             v-html="prettyN(stats.contingency.find(([[ka, kb], e]) => (ka=='pt' && kb=='not_en'))[1])"></td>
                  <th class='number' scope='row' v-html="prettyN(sum(stats.contingency.filter(([[ka, kb], e]) => (ka=='pt')).map(e => e[1])))"></th>
                </tr>
                <tr>
                  <th class="title" scope="row">Synonym</th>
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
              <label for="selecttdata" class="col-sm-3 col-form-label">Plot Data&nbsp;:</label>
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
            title="Repartition of the number of translations per term"
            xtitle="Number of translations"
            ytitle="Number of terms"
            :xdata="statsplotdata.n_trads.map(e => e[0].toFixed(0))"
            :ydata="statsplotdata.n_trads.map(e => e[1])"
          />
        </div>
        <!-- </b-col>
             <b-col sm="12" md="10" lg="8" xl="6" v-if="stats"> -->
        <div class="plot">
          <Barplot
            title="Repartition of the number of wikipedia entries per language"
            xtitle="language"
            ytitle="Number of Wikipedia entries"
            :xdata="statsplotdata.langs.map(e => e[0])"
            :ydata="statsplotdata.langs.map(e => e[1])"
          />
        </div>
      </b-col>
    </b-row>

  </div>
</template>

<script lang="ts">
// import { Component, Vue, Watch } from "vue-property-decorator";
import { Component, Mixins, Prop } from "vue-property-decorator";
import axios from "axios";
import _ from 'lodash';
import Barplot from "@/components/Barplot.vue";
import Boxplot from "@/components/Boxplot.vue";
import { langCodes } from "@/langCodes.js";
import MathMixins from "@/MathMixins";


@Component({
  components: {
    Barplot,
    Boxplot
  },
  mixins: [MathMixins]
})
export default class Stats extends Mixins(MathMixins) { 
  allStats: any = null;
  plotData: string | null = null;
  
  plotDataOptions = [
    {
      text: "All",
      value: null
    },
    {
      text: "English",
      value: "en"
    },
    {
      text: "Everything except english",
      value: "not_en"
    },
    {
      text: "Preferred Term",
      value: "pt"
    },
    {
      text: "Synonym",
      value: "syn"
    },
  ]
  
  matchReportView = "overall"
  get matchReportOptions(){
    return [{text: "All", value: "overall"}].concat(_.sortBy(Object.keys(this.stats.match_report).filter(e => e != "overall").map(e => {
      return {
        text: this.langFromCode(e),
        value: e,
      }
    }), [e => e.text.toLowerCase()]))
  }

  identifier: null | string = null;
  identifiers: string[] = [];
  
  get stats(){
    if(this.allStats && this.identifier){
      return this.allStats[this.identifier]
    }else{
      return null;
    }
  }
  
  get identifierOptions(){
    return this.identifiers.map(e => {
      return {
        text: e,
        value: e
      }
    })
  }

  fetchIdentifiers(){
    axios.get('api/identifiers').then(e => {
      this.identifiers = e.data;
      console.log(this.identifiers)
      this.identifier = this.identifiers[0];
    }).catch(console.log)
  }
  

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
      this.allStats = ans.data
    })
    .catch(console.log);
  }
  mounted() {
    this.fetchIdentifiers();
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
