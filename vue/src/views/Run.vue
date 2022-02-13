<template>
  <div>
    <section class="section">
    <div class="container" v-if="metadata !== null">
      <h1 class="title">{{ accession }}</h1>

      <p class="subtitle">
        {{ metadata.metadata.organism }} ({{ metadata.metadata.librarysource.toLowerCase() }}) | {{ metadata.metadata.sample_name_sam }}
      </p>

      <div>
         {{ metadata.metadata.mbases / 1000}} Gbp | {{ getNumReads }} million reads  | {{ metadata.metadata.avgspotlen }} bp average read length | {{ metadata.metadata.instrument }}
      </div>

      <div>
        NCBI: <a :href="bioproject_url">{{ bioproject_id }}</a> | <a :href="accession">{{ accession }}</a>
      </div>

    </div>
    </section>

    <section>
      <div class="container is-large">
        <h3 class="title">Condensed profile</h3>

        <div class="sunburst">
          <template v-if="condensed_tree != null">
            <Sunburst :json_tree="sunburst_tree" />
          </template>
        </div>
      </div>
    </section>

    <div v-if="metadata !== null">
      <RunMetadata :mdata="metadata.metadata" />
    </div>
  </div>
</template>

<script>

/* eslint-disable vue/no-unused-components */
import Sunburst from '@/components/Sunburst.vue'
import RunMetadata from '@/components/RunMetadata.vue'

import axios from 'axios'

const API_URL = 'http://127.0.0.1:5000/api'

export default {
  name: 'Run',
  data: function () {
    return {
      condensed_tree: null,
      metadata: null
    }
  },
  props: ['accession'],
  components: {
    Sunburst,
    RunMetadata
  },
  computed: {
    bioproject_id: function () {
      return this.metadata.metadata.bioproject_id
    },
    bioproject_url: function () {
      return 'https://www.ncbi.nlm.nih.gov/bioproject/' + this.metadata.metadata.bioproject_id
    },
    getNumReads: function () {
      return Math.round(this.metadata.metadata.mbases / this.metadata.metadata.avgspotlen)
    },
    sunburst_tree: function () {
      return this.condensed_tree.condensed
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
      const accession = this.accession
      console.log('mounting accession: ' + accession)

      axios.get(`${API_URL}/condensed/${accession}`)
        .then(response => {
          this.condensed_tree = response.data
        })

      axios.get(`${API_URL}/metadata/${accession}`)
        .then(response => {
          this.metadata = response.data
        })
    }
  },
  watch: {
    // call again the method if the route changes
    $route: 'fetchData'
  }
}
</script>
