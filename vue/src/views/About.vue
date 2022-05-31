<template>
  <div>
    <section class="section is-small container">
        <p>This is <emph>Sandpiper</emph> version {{ version }}.</p>
        <br />
        <p>It is based a list of public metagenomes which was generated on {{ scrape_date }}.</p>
    </section>

    <section class="section is-small container">
      <h1 class="title">How Sandpiper was built</h1>
      <p>The data underlying Sandpiper was generated using the <a href="https://github.com/wwood/singlem">SingleM</a> pipeline, applied to public metagenome datasets listed in the <a href="https://www.ncbi.nlm.nih.gov/sra">NCBI SRA</a> that were designated as metagenomic, or derived from "metagenomic" organisms such as "soil metagenome".</p>
    </section>

    <section class="section is-small container">
      <h1 class="title">Acknowledgements</h1>
      <p>Development of Sandpiper and SingleM was funded through Australian Research Council Future Fellow (#FT210100521) and Discovery Early Career Research Award (#DE160100248) grants, as well as the <a href="https://emerge-bii.github.io/">EMERGE</a> National Science Foundation (NSF) Biology Integration Institute (#2022070). Cloud computing was generously contributed by Amazon Web Services (AWS) and Google Cloud (GCP).</p>
      <br />
      <p>The sandpiper background image on the front page was derived from <a href="https://www.flickr.com/photos/snarfel/11631543856/in/pool-birds_birds_birds">Frans Vandewalle</a> (CC-NC).</p>
    </section>
  </div>
</template>

<script>
import { fetchSandpiperStats } from '@/api'

export default {
  name: 'About',
  data: function () {
    return {
      num_terrabases: null,
      num_runs: null,
      num_bioprojects: null,
      version: null,
      scrape_date: null
    }
  },
  created () {
    // fetch the data when the view is created and the data is
    // already being observed
    this.fetchData()
  },
  methods: {
    fetchData () {
      fetchSandpiperStats()
        .then(response => {
          const r = response.data
          this.num_terrabases = r.num_terrabases
          this.num_runs = r.num_runs
          this.num_bioprojects = r.num_bioprojects
          this.version = r.version
          this.scrape_date = r.scrape_date
        })
    }
  },
  watch: {
    // call again the method if the route changes
    $route: 'fetchData'
  }
}
</script>
