<template>
  <section class="section container">
    <b-field label="Search for public metagenomes by taxonomy">
      <b-input v-model="taxonomy" icon="magnify" />
    </b-field>
    <b-button type="is-primary" @click="search()">Search</b-button>
    <p>Taxonomy annotations derived from <a href='http://gtdb.ecogenomic.org'>Genome Taxonomy Database (GTDB)</a> version 06-RS202.</p>
  </section>
</template>

<script>
import axios from 'axios'
const API_URL = 'http://127.0.0.1:5000/api'

export default {
  name: 'Search',
  data () {
    return {
      taxonomy: 'p__Actinobacteriota'
    }
  },
  methods: {
    search () {
      const url = `${API_URL}/taxonomy_search/${this.taxonomy}`
      axios.get(url).then(response => {
        this.$router.push({ name: 'SearchResults', params: { taxonomy: this.taxonomy } })
      })
    }
  }
}
</script>
