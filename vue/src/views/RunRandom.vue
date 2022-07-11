<template>
  <div>
    <section class="section container">
      Randomly choosing an accession ..
    </section>
  </div>
</template>

<script>

import { fetchRandomAccession } from '@/api'

export default {
  name: 'Random',
  created () {
    // fetch the data when the view is created and the data is
    // already being observed
    this.fetchData()
  },
  props: [
        'host',
        'ecological',
        'two_gbp'
  ],
  methods: {
    fetchData () {
      fetchRandomAccession(this.host, this.ecological, this.two_gbp)
        .then(response => {
          const acc = response.data.run
          this.$router.push({ name: 'Run', params: { accession: acc } })
        })
    }
  },
  watch: {
    // call again the method if the route changes
    $route: 'fetchData'
  }
}
</script>
