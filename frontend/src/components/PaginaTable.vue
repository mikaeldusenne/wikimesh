<template>
  <b-container fluid>
    <b-row>
      <table
        class="table table-sm table-hover table-striped"
        style="margin-bottom: 0;"
      >
        <thead>
          <tr class="centered">
            <th class="thead-dark" v-for="e in fieldsToUse" :key="e">{{e}}</th>
          </tr>
        </thead>
        <tbody>
          <tr class="centered" v-for="r in recordsSubset">
            <td v-for="e in fieldsToUse">
              {{r[e]}}
            </td>
          </tr>
        </tbody>
      </table>
      <b-pagination
        size="sm"
        class="pagination"
        align="fill"
        v-model="currentPage"
        :total-rows="records.length"
        :per-page="perPage"
      ></b-pagination>

    </b-row>
  </b-container>
</template>

<script lang="ts">
import { Component, Vue, Prop } from "vue-property-decorator";
import { Plotly } from "vue-plotly";
import _ from 'lodash';

@Component({
  components: {
  }
})
export default class Barplot extends Vue {
  @Prop({default: () => []})
  records!: any[];
  
  @Prop({default: null})
  fields!: string[];
  
  @Prop({default: 10})
  perPage!: number;

  currentPage = 1;

  get recordsSubset(){
    return this.records.slice((this.currentPage-1) * this.perPage, (this.currentPage-1) * this.perPage + this.perPage)
  }

  get fieldsToUse(){
    return (this.fields
         && this.fields
         || this.records.map(Object.keys).reduce((acc, e) => {
           return _.uniq(acc.concat(e))
         })
    )
  }
  
}
</script>

<style>
tr.centered > * {
  text-align: center;
}
</style>
