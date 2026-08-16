<template>
  <section id="explorer" class="mx-auto" style="max-width: 950px">
    <h1>Explorer</h1>
    <p>Explore les pages Wikipédia retrouvées pour les concepts MeSH. PT = terme préféré, SYN = synonyme.</p>

    <form class="card card-body mb-4" @submit.prevent="searchData">
      <label class="form-check mb-3">
        <input v-model="filterOnlyNonEmpty" class="form-check-input" type="checkbox" />
        <span class="form-check-label">Masquer les entrées vides</span>
      </label>

      <div class="input-group mb-3">
        <input v-model="search" class="form-control" maxlength="75" placeholder="terme ou identifiant MeSH" />
        <button class="btn btn-outline-secondary">Rechercher</button>
      </div>

      <label class="mb-3">Identifiant
        <select v-model="identifier" class="form-select" @change="searchData">
          <option :value="null">Tous</option>
          <option v-for="value in identifiers" :key="value" :value="value">{{ value }}</option>
        </select>
      </label>

      <template v-if="showAdvancedSearch">
        <div class="row g-3">
          <label class="col-md-6">Langue du match
            <select v-model="langMatchSearch" class="form-select" @change="searchData">
              <option v-for="o in languageOptions" :key="String(o.value)" :value="o.value">{{ o.text }}</option>
            </select>
          </label>
          <label class="col-md-6">Type de match
            <select v-model="ptsynMatchSearch" class="form-select" @change="searchData">
              <option :value="null">PT + SYN</option><option value="pt">PT</option><option value="syn">SYN</option>
            </select>
          </label>
          <label class="col-md-6">Filtrer par langue
            <select v-model="langSearch" class="form-select" @change="searchData">
              <option v-for="o in languageOptions" :key="String(o.value)" :value="o.value">{{ o.text }}</option>
            </select>
          </label>
          <label class="col-md-6">Afficher les liens
            <select v-model="langView" class="form-select">
              <option v-for="o in viewLanguageOptions" :key="String(o.value)" :value="o.value">{{ o.text }}</option>
            </select>
          </label>
        </div>
        <div v-if="langSearch" class="row mt-3">
          <fieldset v-for="[label, model] in [['MeSH', 'mesh'], ['Wikipedia', 'wiki']]" :key="model" class="col-md-6">
            <legend class="fs-6">{{ label }}</legend>
            <label v-for="value in ['yes', 'no', 'all']" :key="value" class="me-3">
              <input v-if="model === 'mesh'" v-model="langMesh" type="radio" :value="value" @change="searchData" />
              <input v-else v-model="langWiki" type="radio" :value="value" @change="searchData" />
              {{ value }}
            </label>
          </fieldset>
        </div>
      </template>

      <div class="d-flex justify-content-between align-items-center mt-3">
        <small>{{ fetching ? 'Recherche…' : `${nMesh} résultat${nMesh === 1 ? '' : 's'}` }}</small>
        <button type="button" class="btn btn-link btn-sm" @click="toggleAdvancedSearch">
          {{ showAdvancedSearch ? 'Recherche simple' : 'Recherche avancée' }}
        </button>
      </div>
    </form>

    <div v-if="metadataError" class="alert alert-warning">
      {{ metadataError }} <button class="btn btn-sm btn-outline-secondary" @click="fetchMetadata">Réessayer</button>
    </div>
    <div v-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-else-if="!fetching && !mesh.length" class="alert alert-secondary">Aucun résultat.</div>

    <div :class="{ fetching }">
      <article v-for="m in mesh" :key="m._id" class="card mb-3">
        <header class="card-header d-flex align-items-center gap-2 flex-wrap">
          <span class="badge text-bg-secondary">{{ m._id }}</span>
          <span v-if="m.wikilangs.origin" class="badge text-bg-success">{{ m.wikilangs.origin.toUpperCase() }}</span>
          <strong :title="matchInfo(m)">{{ m.langs[0]?.pt || m._id }}</strong>
          <small class="text-muted">{{ wikiEntries(m).length }} langues</small>
          <button class="btn btn-sm btn-outline-secondary ms-auto" @click="m.showDetails = !m.showDetails">
            {{ m.showDetails ? 'Masquer' : 'Détails' }}
          </button>
        </header>
        <div class="card-body row g-3">
          <div v-if="m.showDetails" class="col-md-6 scrollbox">
            <strong>Détails du concept</strong>
            <div v-for="lang in m.langs" :key="lang._id" class="mt-2">
              <strong>{{ langFromCode(lang._id) }}:</strong> {{ lang.pt }}
              <small v-if="lang.syns?.length" class="d-block text-muted">Synonymes : {{ lang.syns.join(', ') }}</small>
            </div>
          </div>
          <div class="col scrollbox">
            <strong v-if="m.showDetails">Liens Wikipédia</strong>
            <ul v-if="filterWiki(wikiEntries(m)).length" class="list-unstyled mb-0">
              <li v-for="[lang, title] in filterWiki(wikiEntries(m))" :key="lang" :class="{ 'fw-bold': m.wikilangs.lang_match === lang }">
                <a :href="wikiUrl(lang, title)" target="_blank" rel="noopener">[{{ langFromCode(lang) }}] {{ title }}</a>
              </li>
            </ul>
            <span v-else class="text-muted">Entrée Wikipédia non trouvée.</span>
          </div>
        </div>
      </article>
    </div>

    <nav v-if="pageCount > 1" class="d-flex justify-content-center align-items-center gap-3 sticky-bottom bg-light p-2">
      <button class="btn btn-sm btn-secondary" :disabled="currentPage === 1" @click="currentPage--">Précédent</button>
      <span>{{ currentPage }} / {{ pageCount }}</span>
      <button class="btn btn-sm btn-secondary" :disabled="currentPage === pageCount" @click="currentPage++">Suivant</button>
    </nav>
  </section>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { getJson, requestGate } from "@/api";
import { explorerQuery, pickIdentifier } from "@/explorerState";
import { langCodes } from "@/langCodes.js";

type Option = { text: string; value: string | null };
type Mesh = {
  _id: string;
  langs: Array<{ _id: string; pt: string; syns: string[] }>;
  wikilangs: { origin?: string; lang_match?: string; term_match?: string; langs?: Record<string, string> };
  showDetails?: boolean;
};
type MeshResponse = { count: number; data: Mesh[] };

const route = useRoute(), router = useRouter(), requests = requestGate();
const perPage = 10, nMesh = ref(0), currentPage = ref(1), mesh = ref<Mesh[]>([]);
const search = ref(String(route.query.search || "")), filterOnlyNonEmpty = ref(false);
const fetching = ref(false), error = ref(""), metadataError = ref("");
const showAdvancedSearch = ref(false), langMatchSearch = ref<string | null>(null), ptsynMatchSearch = ref<string | null>(null);
const langSearch = ref<string | null>(null), langView = ref<string | null>(null);
const identifier = ref<string | null>(String(route.query.identifier || "") || null);
const langMesh = ref("all"), langWiki = ref("all"), languages = ref<string[]>([]), identifiers = ref<string[]>([]);

const pageCount = computed(() => Math.max(1, Math.ceil(nMesh.value / perPage)));
const langFromCode = (code: string) => langCodes.find((e: { code: string }) => e.code === code)?.name || code;
const sortedLanguages = computed(() => [...languages.value].sort((a, b) => langFromCode(a).localeCompare(langFromCode(b))));
const languageOptions = computed<Option[]>(() => [
  { text: "Toutes les langues", value: null }, { text: "Toutes sauf anglais", value: "no-english" },
  ...sortedLanguages.value.map(value => ({ text: langFromCode(value), value })),
]);
const viewLanguageOptions = computed(() => languageOptions.value.map(o => o.value === "no-english" ? { ...o, text: "Toutes sauf anglais" } : o));
const wikiEntries = (m: Mesh) => Object.entries(m.wikilangs.langs || {});
const filterWiki = (entries: [string, string][]) => langView.value === null ? entries : entries.filter(([lang]) => langView.value === "no-english" ? lang !== "en" : lang === langView.value);
const wikiUrl = (lang: string, title: string) => `https://${lang}.wikipedia.org/wiki/${encodeURIComponent(title).replaceAll("%20", "_")}`;
const matchInfo = (m: Mesh) => m.wikilangs.lang_match ? `match: (${langFromCode(m.wikilangs.lang_match)}) ${m.wikilangs.term_match || ""}` : "";

async function fetchData() {
  const request = requests.next();
  fetching.value = true; error.value = "";
  try {
    const ans = await getJson<MeshResponse>("api/mesh", {
      from: (currentPage.value - 1) * perPage, limit: perPage, search: search.value,
      filterOnlyNonEmpty: filterOnlyNonEmpty.value, langMatchSearch: langMatchSearch.value,
      ptsynMatchSearch: ptsynMatchSearch.value, langSearch: langSearch.value,
      langMesh: langMesh.value, langWiki: langWiki.value, identifier: identifier.value,
    }, request.signal);
    if (!requests.isCurrent(request)) return;
    nMesh.value = ans.count;
    mesh.value = ans.data.map(m => ({ ...m, showDetails: false }));
    if (currentPage.value > pageCount.value) currentPage.value = pageCount.value;
  } catch (e) {
    if (e instanceof DOMException && e.name === "AbortError") return;
    if (requests.isCurrent(request)) error.value = e instanceof Error ? e.message : "Erreur de chargement";
  } finally {
    if (requests.isCurrent(request)) fetching.value = false;
  }
}

async function fetchMetadata() {
  metadataError.value = "";
  try {
    [languages.value, identifiers.value] = await Promise.all([
      getJson<string[]>("api/languages"), getJson<string[]>("api/identifiers"),
    ]);
    identifier.value = pickIdentifier(identifier.value, identifiers.value);
  } catch (e) { metadataError.value = e instanceof Error ? e.message : "Filtres indisponibles"; }
}

function searchData() {
  void router.replace({ query: explorerQuery(search.value, identifier.value) });
  if (currentPage.value === 1) void fetchData(); else currentPage.value = 1;
}
function toggleAdvancedSearch() {
  showAdvancedSearch.value = !showAdvancedSearch.value;
  localStorage.setItem("showAdvancedSearch", JSON.stringify(showAdvancedSearch.value));
  if (!showAdvancedSearch.value) {
    langMatchSearch.value = ptsynMatchSearch.value = langSearch.value = langView.value = null;
    langMesh.value = langWiki.value = "all";
    searchData();
  }
}
function stored<T>(name: string, fallback: T): T {
  try { const value = localStorage.getItem(name); return value === null ? fallback : JSON.parse(value); }
  catch { return fallback; }
}

watch(currentPage, fetchData);
watch(filterOnlyNonEmpty, searchData);
watch(langMatchSearch, v => localStorage.setItem("langMatchSearch", JSON.stringify(v)));
watch(ptsynMatchSearch, v => localStorage.setItem("ptsynMatchSearch", JSON.stringify(v)));
onMounted(async () => {
  showAdvancedSearch.value = stored("showAdvancedSearch", false);
  langMatchSearch.value = stored("langMatchSearch", null);
  ptsynMatchSearch.value = stored("ptsynMatchSearch", null);
  await fetchMetadata();
  void fetchData();
});
onBeforeUnmount(requests.abort);
</script>

<style scoped>
.fetching { opacity: .55; }
.scrollbox { max-height: 15rem; overflow: auto; }
.sticky-bottom { bottom: 0; z-index: 10; }
</style>
