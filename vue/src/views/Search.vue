<template>
  <section class="section container">

          <p>Sandpiper is a resource for interrogating public microbiome datasets.</p>

      <p>It is currently down for maintenance, we hope to be back soon, within a
      week at least. Thank you for your patience and support.</p>

  </section>
</template>

<script>
// import { fetchTaxonomySearchHints, fetchSandpiperStats } from '@/api'
// import debounce from 'lodash/debounce'

export default {
  name: 'Search',
  title: 'Search - Sandpiper',
  // data () {
  //   return {
  //     gtdb_version: null,

  //     taxonomy: 'c__Bog-38',
  //     autocomplete_taxons: [],
  //     selected: null,
  //     isFetching: false,
  //     accession: 'ERR1914274',

  //     random_choice_host: false,
  //     random_choice_ecological: true,
  //     random_choice_two_gbp: true
  //   }
  // },

  // created () {
  //   // fetch the data when the view is created and the data is
  //   // already being observed
  //   this.fetchData()
  // },

  // watch: {
  //   // Ensure that at least one of host/ecological is on
  //   random_choice_host: function() {
  //     if (!this.random_choice_host) {
  //       this.random_choice_ecological = true
  //     }
  //   },
  //   random_choice_ecological: function() {
  //     if (!this.random_choice_ecological) {
  //       this.random_choice_host = true
  //     }
  //   }
  // },
  
  // methods: {
  //   fetchData () {
  //     fetchSandpiperStats()
  //       .then(response => {
  //         const r = response.data
  //         this.gtdb_version = r.gtdb_version
  //       })
  //   },
  //   search_by_taxonomy () {
  //     this.$router.push({ name: 'SearchResults', params: { taxonomy: this.taxonomy } })
  //   },
  //   getAsyncData: debounce(function (name) {
  //     // if undefined or empty, reset the list
  //     if (name === undefined || name === null || !name.length) {
  //       this.autocomplete_taxons = []
  //       return
  //     }
  //     this.isFetching = true
  //     fetchTaxonomySearchHints(name)
  //       .then(({ data }) => {
  //         this.autocomplete_taxons = data.taxonomies
  //         if (this.autocomplete_taxons != undefined && this.autocomplete_taxons.length >= 30) {
  //           this.autocomplete_taxons.push('.. possibly more')
  //         }
  //       })
  //       .catch((error) => {
  //         this.autocomplete_taxons = []
  //         throw error
  //       })
  //       .finally(() => {
  //         this.isFetching = false
  //       })
  //   }, 500),

  //   search_by_accession() {
  //     const uppercaseAccession = this.accession.toUpperCase();
  //     this.$router.push({ name: 'Accession', params: { accession: uppercaseAccession } });
  //   },

  //   search_by_random () {
  //     this.$router.push({ name: 'RunRandom', query: { 
  //       host: this.random_choice_host,
  //       ecological: this.random_choice_ecological,
  //       two_gbp: this.random_choice_two_gbp
  //     }})
  //   }
  // }
}
</script>
