<template>
  <section class="section container" @keyup.enter="search">
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
    <b-button type="is-primary" @click="search">Search</b-button>
    <br />
    <br />
    <p>Taxonomy annotations derived from <a href='http://gtdb.ecogenomic.org'>Genome Taxonomy Database (GTDB)</a> version 06-RS202.</p>
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
      isFetching: false
    }
  },
  methods: {
    search () {
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
    }, 500)
  }
}
</script>
