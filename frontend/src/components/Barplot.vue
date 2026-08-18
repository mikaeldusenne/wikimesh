<template>
  <figure>
    <figcaption class="fw-bold mb-2">{{ title }}</figcaption>
    <div v-if="unavailable" class="alert alert-warning">Graphique Plotly indisponible.</div>
    <div v-show="!unavailable" ref="plot" class="plot" />
  </figure>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from "vue";

type PlotlyApi = {
  react: (element: HTMLElement, data: unknown[], layout: Record<string, unknown>, config: Record<string, unknown>) => void;
  purge: (element: HTMLElement) => void;
};

declare global { interface Window { Plotly?: PlotlyApi } }

const props = defineProps<{
  title: string;
  xtitle: string;
  ytitle: string;
  xdata: Array<string | number>;
  ydata: number[];
}>();

const plot = ref<HTMLElement>();
const unavailable = ref(false);

function draw() {
  if (!plot.value) return;
  if (!window.Plotly) {
    unavailable.value = true;
    return;
  }
  unavailable.value = false;
  window.Plotly.react(
    plot.value,
    [{ type: "bar", x: props.xdata, y: props.ydata, hovertemplate: "%{x}: %{y}<extra></extra>" }],
    {
      autosize: true,
      margin: { l: 70, r: 20, t: 10, b: 70 },
      xaxis: { title: { text: props.xtitle }, automargin: true },
      yaxis: { title: { text: props.ytitle }, automargin: true },
    },
    { responsive: true, displaylogo: false },
  );
}

watch(() => [props.xdata, props.ydata, props.xtitle, props.ytitle], draw, { deep: true });
onMounted(draw);
onBeforeUnmount(() => { if (plot.value && window.Plotly) window.Plotly.purge(plot.value); });
</script>

<style scoped>
.plot { min-height: 420px; width: 100%; }
</style>
