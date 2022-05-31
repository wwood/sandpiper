<template>
  <div>
    <div v-if="metadata !== null">
      <section class="section">
      <div class="container" v-if="metadata !== null">
        <h1 class="title">{{ metadata.metadata.study_title }}</h1>

        <p class="subtitle">
          Sample {{ sample_name_mature }}
        </p>

        <div>
          {{ metadata.metadata.organism }} | {{ metadata.metadata.librarysource.toLowerCase() }} | {{ metadata.metadata.mbases / 1000}} Gbp | {{ getNumReads }} million reads  | {{ metadata.metadata.avgspotlen }} bp average read length | {{ metadata.metadata.instrument }}
          <br />
          NCBI: <a :href="bioproject_url">{{ bioproject_id }}</a> | <a :href="'http://www.ncbi.nlm.nih.gov/sra?term=' + accession">{{ accession }}</a>
          <br />
        </div>

        <div>
          <br />
          <p>{{ metadata.metadata.study_abstract }}</p>
        </div>

        <div>
          <br />
          <div v-if="metadata.metadata.study_links.length===0">
            <p>No linked publications recorded.</p>
          </div>
          <div v-else>
            <ul v-for="link in metadata.metadata.study_links" v-bind:key="link.study_id">
              <li v-if="link['database'].toLowerCase()==='pubmed'">PubMed <a :href="'https://www.ncbi.nlm.nih.gov/pubmed?term='+link['study_id']">{{ link['study_id'] }}</a></li>
              <li v-else>{{ link['database'] }} {{ link['study_id'] }}</li>
            </ul>
          </div>
        </div>
      </div>
      </section>

      <section>
        <div class="container is-large">
          <h3 class="title">Condensed profile</h3>

          <div class="sunburst">
            <template v-if="condensed_tree != null">
              <Sunburst3 :json_tree="sunburst_tree" :overall_coverage="10.3" />
            </template>
          </div>
        </div>
      </section>

      <RunMetadata :mdata="metadata.metadata" />
    </div>

    <div v-else>
      <div v-if="error_message !== null">
        <section class="section container">
          <b-message 
            title="Error" 
            type="is-warning" 
            :closable="false"
            has-icon>
            <p>ERROR {{ error_message }}</p>
          </b-message>
        </section>
      </div>

      <div v-else>
        <section class="section container">
          Searching ..
        </section>
      </div>
    </div>
  </div>
</template>

<script>

/* eslint-disable vue/no-unused-components */
import Sunburst3 from '@/components/Sunburst3.vue'
import RunMetadata from '@/components/RunMetadata.vue'

import { fetchRunMetadata, fetchRunCondensed } from '@/api'

export default {
  name: 'Run',
  data: function () {
    return {
      condensed_tree: null,
      metadata: null,
      error_message: null
    }
  },
  props: ['accession'],
  components: {
    Sunburst3,
    RunMetadata
  },
  computed: {
    bioproject_id: function () {
      return this.metadata.metadata.bioproject
    },
    bioproject_url: function () {
      return 'https://www.ncbi.nlm.nih.gov/bioproject/' + this.metadata.metadata.bioproject_id
    },
    getNumReads: function () {
      return Math.round(this.metadata.metadata.mbases / this.metadata.metadata.avgspotlen)
    },
    sunburst_tree: function () {
      return this.condensed_tree.condensed
    },
    sample_name_mature: function () {
      if (this.metadata.metadata.sample_name_sam !== null) {
        return this.metadata.metadata.sample_name_sam
      } else {
        return this.metadata.metadata.sample_name
      }
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

      fetchRunCondensed(accession)
        .then(response => {
          this.condensed_tree = response.data
        })

      fetchRunMetadata(accession)
        .then(response => {
          if (response.data.error !== undefined) {
            this.error_message = response.data.error
          } else {
            this.metadata = response.data
          }
        })
    },
    study_toplink (link) {
      if (link['database'].toLowerCase()==='pubmed') {
        return '<a href="https://www.ncbi.nlm.nih.gov/pubmed?term='+link['study_id']+'">'+link['study_id']+'</a>'
      } else {
        return link['database'] + ': ' + link['study_id']
      }
      return 'link'
    }
  },
  watch: {
    // call again the method if the route changes
    $route: 'fetchData'
  }
}
</script>
