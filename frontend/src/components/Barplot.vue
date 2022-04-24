<template>
  <Plotly
    :data="traces"
    :layout="layout"
  ></Plotly>
</template>

<script lang="ts">
import { Component, Vue, Prop } from "vue-property-decorator";
import { Plotly } from "vue-plotly";
import _ from 'lodash';

@Component({
  components: {
    Plotly,
  }
})
export default class Barplot extends Vue {
  stats: any = {};
  
  font: any = {
    family: 'Source Code Pro',
    color: "#000",
    size: 11,
  }
  
  @Prop({default: ""})
  xtitle!: string;
  
  @Prop({default: ""})
  ytitle!: string;
  
  @Prop({default: ""})
  title!: string;
  
  @Prop({default: () => []})
  xdata!: string;
  
  @Prop({default: () => []})
  ydata!: string;
  
  layout = {
    height: 350,
    responsive: true,
    barmode: "stack",
    plot_bgcolor: "#fff",
    paper_bgcolor: "#fff",
    font: this.font,
    legend: {
      xanchor: "right",
      x: 0.25,
      y: 1.2
    },
    margin:{
      l: 70,
      r: 70, 
      b: 70,
      t: 70
    },
    title: {
      text: this.title,
      font: {...this.font, ...{size: 12}},
      xref: 'paper',
      x: 100,
    },
    xaxis: {
      tickfont: this.font,
      title: {
        text: this.xtitle,
        font: this.font,
      },
      linecolor: '#000',
      tickcolor: '#000',

      visible: true,
      // nticks: 10,
      // ticktext: this.dates.map(e => e.toLocaleDateString())
    },
    yaxis: {
      tickfont: this.font,
      title: {
        text: this.ytitle,
        font: this.font,
      },
      linecolor: '#000',
      tickcolor: '#000',
      gridcolor: "#111",
      // type: "log",
      autorange: true,
      visible: true,

    }
  };
  
  
  get traces(){
    return [{
      x: this.xdata,
      y: this.ydata,
      name: "",
      type: 'bar',
      // width: 1000*3600*24*2,
      width: 0.9,
      hoverinfo: 'text+x+y',
      marker: {
        color: "#1793d0",
        line: {
          color: "#1793d022",
          width: 1.5,
        }
      }
    }]
  }
}
</script>

<style>
</style>
