<template>
  <div class="sandpiperbackground">
    <section class="section container" v-if="num_terrabases!==null" >
      <!-- <h1 class="title">{{ num_runs.toLocaleString("en-US") }} metagenomes screened.</h1>
      <h2 class="subtitle">{{ num_terrabases.toLocaleString("en-US") }} Tbp and {{ num_bioprojects.toLocaleString("en-US") }} projects</h2> -->

      <p>Sandpiper is a resource for interrogating public microbiome datasets.</p>

      <p>It is currently down for maintenance, we hope to be back soon, within a
      week at least. Thank you for your patience and support.</p>
    </section>

    <section class="section container is-large" />
  </div>
</template>

<script>
// import { fetchSandpiperStats } from '@/api'

export default {
  name: 'Home',
  title: 'Sandpiper',
  // data: function () {
  //   return {
  //     num_terrabases: null,
  //     num_runs: null,
  //     num_bioprojects: null,
  //     version: null
  //   }
  // },
  // created () {
  //   // fetch the data when the view is created and the data is
  //   // already being observed
  //   this.fetchData()
  // },
  // methods: {
  //   fetchData () {
  //     fetchSandpiperStats()
  //       .then(response => {
  //         const r = response.data
  //         this.num_terrabases = r.num_terrabases
  //         this.num_runs = r.num_runs
  //         this.num_bioprojects = r.num_bioprojects
  //         this.version = r.version
  //       })
  //   }
  // },
  // watch: {
  //   // call again the method if the route changes
  //   $route: 'fetchData'
  // }
}
</script>
