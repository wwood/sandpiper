<template>
<div>
      <section class="section is-medium container">
        <h1 class="title">How Sandpiper was built</h1>
        <p>The data underlying Sandpiper was generated using the <a href="https://github.com/wwood/singlem">SingleM</a> pipeline, applied to public metagenome datasets listed in the <a href="https://www.ncbi.nlm.nih.gov/sra">NCBI SRA</a> that were designated as metagenomic, or derived from "metagenomic" organisms such as "soil metagenome".</p>
      </section>

      <section class="section is-medium container">
        <h1 class="title">Acknowledgements</h1>
        <p>Development of Sandpiper and SingleM was funded through Australian Research Council Future Fellow (#FT210100521) and Discovery Early Career Research Award (#DE160100248) grants, as well as the <a href="https://emerge-bii.github.io/">EMERGE</a> National Science Foundation (NSF) Biology Integration Institute (#2022070). Cloud computing was generously contributed by Amazon Web Services (AWS) and Google Cloud (GCP).</p>
        <p>The sandpiper background image on the front page was derived from <a href="https://www.flickr.com/photos/snarfel/11631543856/in/pool-birds_birds_birds">Frans Vandewalle</a> (CC-NC).</p>
      </section>
      </div>
</template>

<script lang="ts">
export default {
  name: 'About'
}
</script>
