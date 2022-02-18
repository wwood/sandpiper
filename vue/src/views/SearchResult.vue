<template>
  <section class="section container" v-if="search_result !== null">
    <div v-if="('condensed_profiles' in search_result)">
      Found {{ search_result['condensed_profiles'].length }} runs containing "<i>{{ taxonomy }}</i>"
      <b-table :data="search_result['condensed_profiles']" :striped="true" :sort-icon="'arrow-up'" default-sort="relative_abundance" :default-sort-direction="'desc'">

        <b-table-column field='sample_name' label='Run' v-slot="props">
          <a :href="'/run/' + props.row.sample_name">{{ props.row.sample_name }}</a>
        </b-table-column>

        <b-table-column field='relative_abundance' label='Relative abundance (%)' v-slot="props" centered sortable>
          {{ props.row.relative_abundance }}
        </b-table-column>

        <b-table-column field='coverage' label='Coverage' v-slot="props" centered sortable>
          {{ props.row.coverage }}
        </b-table-column>
      </b-table>
    </div>
    <div v-else>
      {{ search_result['taxon'] }}
    </div>
  </section>
  <section class="section container" v-else>
    Searching ..
  </section>
</template>

<script>
import axios from 'axios'
const API_URL = 'http://127.0.0.1:5000/api'

export default {
  name: 'SearchResults',
  props: ['taxonomy'],
  data: function () {
    return {
      search_result: null,
      sortIcon: 'arrow-up'
    }
  },
  created () {
    // fetch the data when the view is created and the data is
    // already being observed
    this.fetchData()
  },
  methods: {
    fetchData () {
      // const accession = this.$route.params.accession
      const taxonomy = this.taxonomy

      axios.get(`${API_URL}/taxonomy_search/${taxonomy}`)
        .then(response => {
          this.search_result = response.data
        })
    },
    numericColumnTdAttrs (row, column) {
      return {
        style: 'text-align: center;'
      }
    }
  },
  watch: {
    // call again the method if the route changes
    $route: 'fetchData'
  }
}
</script>
