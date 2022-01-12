<template>
  <div class="container-fluid" v-if="stats">
    <b-row class="justify-content-md-center">
      <b-col class="col-md-6">
        <h1>Statistics</h1>
        <p>
          Descriptive stats of the wikipedia entries found. 
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
      
      <div class="row justify-content-md-center" style="margin: 1rem;"  v-on:submit.prevent>
        <b-col sm="12" md="8" lg="6" xl="6" style="margin: 0; padding: 0;">
          <div class="card">
            <!-- <div class="card-header">
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
                 </div> -->
            <div class="card-body">
              <p>
                
                <!-- <div v-if="matchReportView != 'overall'">
                     Among the {{identifier}} terms in <span class="number">{{langFromCode(matchReportView)}}</span>,
                     </div>
                     <div v-else>
                     Among all languages of all {{identifier}} terms,
                     </div> -->
                <br>
                <span>Number of pre-existing languages per MeSH Term in our database: </span><span style="display: inline;" v-html="describeStats(stats.mesh_terms_stats.mesh)" /> <br />
                <span>Number of detected Wikipedia languages per MeSH Term:</span> <span v-html="describeStats(stats.mesh_terms_stats.wiki)" />.
                <div class="plot">
                  <Barplot
                    title="Number of languages per MeSH descriptor"
                    xtitle="Number of languages (Wikipedia pages)"
                    ytitle="MeSH descriptors"
                    :xdata="statsplotdata.n_trads.map(e => e[0].toFixed(0))"
                    :ydata="statsplotdata.n_trads.map(e => e[1])"
                  />
                </div>
                
                <!-- <span>Number of pre-existing languages per MeSH Term in our database: </span><span style="display: inline;" v-html="describeStats(stats.mesh_terms_stats.mesh)" /> <br /> -->
                Number of added language thanks to our method: <span v-html="describeStats(calcStats(expandArray(stats.new_langs)))" />
                
                <div class="plot">
                  <Barplot
                    title="Repartition of the number of new languages per term found by our method "
                    xtitle="Number of new languages"
                    ytitle="Number of MeSH Terms"
                    :xdata="stats.new_langs.filter(e => e[0] > 0).map(e => e[0])"
                    :ydata="stats.new_langs.filter(e => e[0] > 0).map(e => e[1])"
                  />
                </div>
              </p>
              <p>
                For <span class="number" v-html="prettyN(stats.origins.pt || 0)" /> {{identifier}} terms, the Preferred Term matched the wikipedia entry.<br>
                For <span class="number" v-html="prettyN(stats.origins.syn || 0)" /> {{identifier}} terms, one of the synonyms matched the wikipedia entry.
              </p><br />
              <!-- Number of wikipedia pages per language: <span v-html="describeStats(calcStats(statsplotdata.langs.map(e => e[1])))" /> -->
              The most frequent languages are: <span class="number" v-for="e in top10lang">{{e}}</span>
              <div class="plot">
                <Barplot
                  title="Repartition of the number of wikipedia entries per language"
                  xtitle="language"
                  ytitle="Number of Wikipedia entries"
                  :xdata="statsplotdata.langs.map(e => e[0])"
                  :ydata="statsplotdata.langs.map(e => e[1])"
                />
              </div>

            </div>
          </div>
        </b-col>
        
      </div>
    </div>

    <div class="row justify-content-md-center" style="margin: 1rem;" v-on:submit.prevent>
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
    // {
    //   text: "English",
    //   value: "en"
    // },
  // {
    //   text: "Everything except english",
    //   value: "not_en"
    // },
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

  identifier: null | string = "MeSH";
  identifiers: string[] = [];

  calcStats(l){
    return {
      mean: this.mean(l),
      sd: this.sd(l),
      min: Math.min(...l),
      max: Math.max(...l),
    }
  }
  
  describeStats(o){
    return '<span class="number">' + this.prettyN(o.mean.toFixed(2)) + "</span> &#177; " + '<span class="number">' + this.prettyN(o.sd.toFixed(2)) + "</span> (min-max: "+ '<span class="number">' + o.min +"</span>&nbsp;-&nbsp;"+'<span class="number">' + o.max +"</span>) "
  }
  
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
  
  expandArray(l){
    return l.reduce((acc, [k, v]) => {
      return acc.concat(Array(v).fill(k))
    }, [])
  }
  
  fetchIdentifiers(){
    axios.get('api/identifiers').then(e => {
      this.identifiers = e.data;
      console.log(this.identifiers)
      // this.identifier = this.identifiers[0];
    }).catch(console.log)
  }
  

  get statsplotdata(){
    return this.stats[this.plotData || "all"];
  }
  
  font: any = {
    family: 'Source Code Pro',
    color: "#000",
  }
  
  sum(l){
    return !l?0:l.length==1?l[0]:l.reduce((a, b) => a+b)
  }
  
  get top10lang(){
    return this.statsplotdata.langs.slice(0, 10).map(e => e[0] ).map(e => {
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
      // console.log(JSON.stringify(ans.data.MeSH, null, 2));
      console.log(ans.data);
      console.log(ans.data.MeSH);
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

<style >
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
