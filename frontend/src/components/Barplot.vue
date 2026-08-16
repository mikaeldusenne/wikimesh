<template>
  <figure>
    <figcaption class="fw-bold mb-2">{{ title }}</figcaption>
    <div v-for="([label, value]) in rows" :key="label" class="bar-row" :title="`${label}: ${value}`">
      <span class="label">{{ label }}</span>
      <span class="bar"><i :style="{ width: `${100 * value / max}%` }" /></span>
      <span class="value">{{ value }}</span>
    </div>
    <small class="text-muted">{{ xtitle }} · {{ ytitle }}</small>
  </figure>
</template>

<script setup lang="ts">
import { computed } from "vue";
const props = defineProps<{ title: string; xtitle: string; ytitle: string; xdata: Array<string | number>; ydata: number[] }>();
const rows = computed(() => props.xdata.map((x, i) => [String(x), props.ydata[i] || 0] as const));
const max = computed(() => Math.max(1, ...props.ydata));
</script>

<style scoped>
.bar-row { display: grid; grid-template-columns: minmax(4rem, 9rem) 1fr 4rem; gap: .5rem; align-items: center; margin: .25rem 0; }
.label { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.bar { height: .8rem; background: #ddd; }
.bar i { display: block; height: 100%; background: #666; }
.value { text-align: right; font-family: monospace; }
</style>
