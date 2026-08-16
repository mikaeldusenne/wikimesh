<template>
  <section class="mx-auto" style="max-width: 850px">
    <h1>Methodology</h1>
    <p>
      The goal of this tool is to find Wikipedia entries in different languages for terms of the
      <a href="https://www.hetop.eu/hetop/rep/uk/MESH/" target="_blank" rel="noopener">MeSH thesaurus</a>.
    </p>
    <p>
      The <a href="https://www.mediawiki.org/wiki/API:Main_page" target="_blank" rel="noopener">Wikipedia API</a>
      exposes linguistic links for a page, allowing one topic to be explored in different languages.
    </p>
    <p>For each MeSH concept, the search stops at the first successful strategy:</p>
    <ol>
      <li>Search its English preferred term.</li>
      <li>Search its English synonyms.</li>
      <li>Repeat preferred-term then synonym searches in the other available languages.</li>
    </ol>
    <p>The language links of the first matching Wikipedia page are retained.</p>
  </section>
</template>

<style scoped>li { margin-bottom: .75rem; }</style>
