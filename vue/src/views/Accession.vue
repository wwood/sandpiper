<template>
  <div v-if="error_message !== null">
    <section class="section container">
      <b-message 
        title="Error" 
        type="is-warning" 
        :closable="false"
        has-icon>
        <p>{{ error_message }}</p>
      </b-message>
    </section>
  </div>

  <div v-else>
      <section class="section container">
        Searching for accession {{ accession }} ..
      </section>
  </div>
</template>

<script>

import { fetchAccession } from '@/api'

export default {
  name: 'Accession',
  title: 'Accession search - Sandpiper',
  created () {
    // fetch the data when the view is created and the data is
    // already being observed
    this.fetchData()
  },
  data () {
    return {
      error_message: null
    }
  },
  props: [
    'accession'
  ],
  methods: {
    fetchData () {
      fetchAccession(this.accession)
        .then(response => {
          const result_type = response.data.result_type
          if (result_type === 'fail') {
            this.error_message = response.data.error
          } else {
            const acc = response.data.accession
            if (result_type === 'run') {
              this.$router.push({ name: 'Run', params: { accession: acc } })
            } else if (result_type === 'project') {
              this.$router.push({ name: 'Project', query: { model_bioproject: acc } })
            } else {
              console.log("Failed result_type: " + result_type)
            }
          }
        })
    }
  },
  watch: {
    // call again the method if the route changes
    $route: 'fetchData'
  }
}
</script>
