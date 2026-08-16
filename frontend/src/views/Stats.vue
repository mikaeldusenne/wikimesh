<template>
  <section class="mx-auto" style="max-width: 950px">
    <h1>Statistiques</h1>
    <p>Statistiques descriptives des entrées Wikipédia trouvées.</p>
    <div v-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-else-if="!stats" class="text-muted">Chargement…</div>

    <template v-else>
      <label class="mb-3">Identifiant
        <select v-model="identifier" class="form-select">
          <option v-for="id in identifiers" :key="id" :value="id">{{ id }}</option>
        </select>
      </label>

      <div class="card mb-4">
        <div class="card-header d-flex justify-content-between align-items-center gap-3">
          <strong>{{ identifier }} / Wikipédia</strong>
          <select v-model="matchReportView" class="form-select form-select-sm" style="max-width: 16rem">
            <option v-for="o in matchReportOptions" :key="o.value" :value="o.value">{{ o.text }}</option>
          </select>
        </div>
        <div class="card-body">
          <p v-if="matchReport">
            <N :value="matchReport.not_in_wiki" /> sans page Wikipédia ·
            <N :value="matchReport.not_in_mesh" /> sans traduction {{ identifier }} ·
            <N :value="matchReport.no_match" /> sans correspondance PT/SYN.
          </p>
          <p v-if="matchReport">
            <N :value="matchReport.pt" /> correspondances par terme préféré ·
            <N :value="matchReport.syn" /> par synonyme.
          </p>
        </div>
      </div>

      <p>
        <N :value="stats.overall?.zero" /> / <N :value="stats.overall?.n" /> concepts
        ({{ percent(stats.overall?.zero_frac) }}) n'ont pas de page Wikipédia associée.
      </p>
      <p>
        Nombre moyen de traductions : <N :value="stats.overall?.mean" />
        (ET = <N :value="stats.overall?.sd" />).
      </p>
      <p>Langues les plus fréquentes : {{ topLanguages.join(', ') }}.</p>

      <label class="mb-4">Données des graphiques
        <select v-model="plotData" class="form-select">
          <option :value="null">Tout</option><option value="en">Anglais</option><option value="not_en">Hors anglais</option>
          <option value="pt">Terme préféré</option><option value="syn">Synonyme</option>
        </select>
      </label>

      <Barplot v-if="translationsChart.length" class="mb-5"
        title="Nombre de traductions par terme" xtitle="Traductions" ytitle="Termes"
        :xdata="translationsChart.map(e => e[0])" :ydata="translationsChart.map(e => e[1])" />
      <Barplot v-if="languageChart.length"
        title="Entrées Wikipédia par langue" xtitle="Langue" ytitle="Entrées"
        :xdata="languageChart.map(e => langFromCode(e[0]))" :ydata="languageChart.map(e => e[1])" />
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, defineComponent, h, onMounted, ref, watch } from "vue";
import Barplot from "@/components/Barplot.vue";
import { getJson } from "@/api";
import { langCodes } from "@/langCodes.js";

type Pair = [string, number];
const allStats = ref<Record<string, any>>({}), identifiers = ref<string[]>([]), identifier = ref("");
const matchReportView = ref("overall"), plotData = ref<string | null>(null), error = ref("");
const stats = computed(() => allStats.value[identifier.value]);
const plotStats = computed(() => plotData.value ? stats.value?.[plotData.value] : stats.value);
const langFromCode = (code: string) => langCodes.find((e: { code: string }) => e.code === code)?.name || code;
const matchReportOptions = computed(() => Object.keys(stats.value?.match_report || {}).sort((a, b) => a === "overall" ? -1 : langFromCode(a).localeCompare(langFromCode(b))).map(value => ({ value, text: value === "overall" ? "Toutes les langues" : langFromCode(value) })));
const matchReport = computed(() => stats.value?.match_report?.[matchReportView.value]);
const topLanguages = computed(() => (stats.value?.langs || []).slice(0, 10).map((e: Pair) => langFromCode(e[0])));
const translationsChart = computed<Pair[]>(() => plotStats.value?.n_trads || []);
const languageChart = computed<Pair[]>(() => plotStats.value?.langs || []);
const percent = (value = 0) => `${(100 * value).toFixed(2)} %`;
const format = (value: unknown) => Number(value || 0).toLocaleString(undefined, { maximumFractionDigits: 0 });
const N = defineComponent({ props: { value: { required: false } }, setup: p => () => h("span", { class: "number" }, format(p.value)) });

watch(identifier, () => { matchReportView.value = "overall"; plotData.value = null; });
onMounted(async () => {
  try {
    [identifiers.value, allStats.value] = await Promise.all([
      getJson<string[]>("api/identifiers"), getJson<Record<string, any>>("api/mesh-stats"),
    ]);
    identifier.value = identifiers.value[0] || Object.keys(allStats.value)[0] || "";
  } catch (e) { error.value = e instanceof Error ? e.message : "Statistiques indisponibles"; }
});
</script>

<style scoped>
.number { font-family: monospace; background: #ddd; padding: .15rem .35rem; border-radius: .2rem; }
</style>
