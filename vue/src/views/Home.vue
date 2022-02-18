<template>
  <section class="section container" v-if="num_terrabases!==null">
    <p>Sandpiper is a website for interrogating public metagenome datasets,
    presenting the results of <a href="https://github.com/wwood/singlem">SingleM</a>
    as applied to {{ num_terrabases }} Tbp from {{ num_runs }} runs and {{ num_bioprojects }}
    projects.</p>

    <p>The authors gratefully acknowledge the large collective effort expended
    in administering, gathering, sequencing and uploading these datasets into
    the public domain.</p>
  </section>
</template>

<script lang="ts">
import axios from 'axios'
const API_URL = 'http://127.0.0.1:5000/api'

export default {
  name: 'Home',
  data: function () {
    return {
      num_terrabases: null,
      num_runs: null,
      num_bioprojects: null
    }
  },
  created () {
    // fetch the data when the view is created and the data is
    // already being observed
    this.fetchData()
  },
  methods: {
    fetchData () {
      axios.get(`${API_URL}/sandpiper_stats`)
        .then(response => {
          const r = response.data
          console.log(r)
          this.num_terrabases = r.num_terrabases
          this.num_runs = r.num_runs
          this.num_bioprojects = r.num_bioprojects
        })
    }
  },
  watch: {
    // call again the method if the route changes
    $route: 'fetchData'
  }
}
</script>
