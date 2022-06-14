<template>
  <section class="section container">

    <section class="section" @keyup.enter="search_by_taxonomy">
      <b-field label="Search for public metagenomes by taxonomy">
        <b-autocomplete v-model="taxonomy" rounded
          max-height="600px"
          icon="magnify"
          :data="autocomplete_taxons"
          :loading="isFetching"
          @typing="getAsyncData">
          <template #empty>No results found</template>
        </b-autocomplete>
      </b-field>
      <b-button type="is-primary" @click="search_by_taxonomy">Search</b-button>
      <br />
      <br />
      <p>Taxonomy annotations derived from <a href='http://gtdb.ecogenomic.org'>Genome Taxonomy Database (GTDB)</a> version 06-RS202.</p>
    </section>

    <section class="section"  @keyup.enter="search_by_accession">
      <b-field label="Search for run accession">
        <b-input v-model="accession"></b-input>
      </b-field>
      <b-button type="is-primary" @click="search_by_accession">Search</b-button>
      <br />
      <br />
    </section>


    <section class="section"  @keyup.enter="search_by_random">
      <b-field label="Inspect a randomly chosen run">
        <b-switch v-model="random_choice_host">Host-associated</b-switch>
        <b-switch v-model="random_choice_ecological">Ecological</b-switch>
        <b-switch v-model="random_choice_two_gbp">2+ Gbp</b-switch>
      </b-field>
      <b-button type="is-primary" @click="search_by_random">Search</b-button>
      <br />
      <br />
    </section>

  </section>
</template>

<script>
import { fetchTaxonomySearchHints } from '@/api'
import debounce from 'lodash/debounce'

export default {
  name: 'Search',
  data () {
    return {
      taxonomy: 'c__Bog-38',
      autocomplete_taxons: [],
      selected: null,
      isFetching: false,
      accession: 'ERR1914274',

      random_choice_host: false,
      random_choice_ecological: true,
      random_choice_two_gbp: true
    }
  },

  watch: {
    // Ensure that at least one of host/ecological is on
    random_choice_host: function() {
      if (!this.random_choice_host) {
        this.random_choice_ecological = true
      }
    },
    random_choice_ecological: function() {
      if (!this.random_choice_ecological) {
        this.random_choice_host = true
      }
    }
  },
  
  methods: {
    search_by_taxonomy () {
      this.$router.push({ name: 'SearchResults', params: { taxonomy: this.taxonomy } })
    },
    getAsyncData: debounce(function (name) {
      if (!name.length) {
        this.autocomplete_taxons = []
        return
      }
      this.isFetching = true
      fetchTaxonomySearchHints(name)
        .then(({ data }) => {
          this.autocomplete_taxons = data.taxonomies
          if (this.autocomplete_taxons.length >= 30) {
            this.autocomplete_taxons.push('.. possibly more')
          }
        })
        .catch((error) => {
          this.autocomplete_taxons = []
          throw error
        })
        .finally(() => {
          this.isFetching = false
        })
    }, 500),

    search_by_accession () {
      this.$router.push({ name: 'Run', params: { accession: this.accession } })
    },

    search_by_random () {
      this.$router.push({ name: 'RunRandom', params: { 
        host: this.random_choice_host,
        ecological: this.random_choice_ecological,
        two_gbp: this.random_choice_two_gbp
      }})
    }
  }
}
</script>
