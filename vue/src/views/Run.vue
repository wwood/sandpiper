<template>
  <div>
    <div v-if="metadata !== null">
      <section class="section">
        <div class="container" v-if="metadata !== null">
          <h1 class="title">{{ metadata.metadata_parsed.study_title }}</h1>

          <p class="subtitle">
            Sample {{ sample_name_mature }}
          </p>

          <div>
            {{ metadata.metadata_parsed.organism }} | {{
            metadata.metadata_parsed.mbases / 1000}} Gbp | {{ getNumReads }} million
            reads {{ read_length_mature }}|
            {{ metadata.metadata_parsed.instrument }} | Released {{
            metadata.metadata_parsed.release_month }} | 
            <span v-if="metadata.metadata_parsed.num_related_runs == 0">No related runs here.</span>
            <span v-else>
              <router-link :to="{ name: 'Project', query: { model_bioproject: metadata.metadata_parsed.bioproject }}">
                <span v-if="metadata.metadata_parsed.num_related_runs == 1">1 related run</span>
                <span v-else>1
                  {{ metadata.metadata_parsed.num_related_runs }} related runs
                </span>
               </router-link>
              </span>
      <!-- {{ related_runs_short }}  -->
            <br />
            NCBI: <a :href="bioproject_url">{{ metadata.metadata_parsed.bioproject }}</a> | <a :href="'http://www.ncbi.nlm.nih.gov/sra?term=' + accession">{{ accession }}</a>
            <br />
          </div>

          <div class="has-text-justified">
            <br />
            <p>{{ metadata.metadata_parsed.study_abstract }}</p>
          </div>

          <div>
            <br />
            <div v-if="publications.length===0">
              <p>No linked publications recorded. A <a :href="scholar_search_url">search on Google Scholar</a> may find some.</p>
            </div>
            <div v-else>
              <ul v-for="link in publications" v-bind:key="link.study_id">
                <li v-if="link['database'].toLowerCase()==='pubmed'">PubMed <a :href="'https://www.ncbi.nlm.nih.gov/pubmed?term='+link['study_id']">{{ link['study_id'] }}</a></li>
                <li v-else>{{ link['database'] }} {{ link['study_id'] }}</li>
              </ul>
              A <a :href="scholar_search_url">search on Google Scholar</a> may find further publications.
            </div>
          </div>

          <div v-if="non_publication_study_links.length>0">
            <br />
            This run has links to other databases:
            <ul v-for="link in non_publication_study_links" v-bind:key="link.label">
              <li><b-icon icon="link-variant" size="is-small" /><a :href="link.url">{{link.label}}</a></li>
            </ul>
          </div>
        </div>
      </section>

      <section class="section">
        <div class="container">
          <h3 class="title">Condensed profile</h3>

          <div class="sunburst">
            <template v-if="condensed_tree != null">
              <Sunburst3 :json_tree="sunburst_tree" :overall_coverage="10.3" />
            </template>
          </div>
        </div>
      </section>

      <section class="section">
        <div class="container is-large">
          <h3 class="title">Full SingleM profile</h3>
          
          <p>The <a :href="full_profile_link">full SingleM OTU profile of {{ accession }}</a> is a tab-separated file containing information about each OTU from each marker, and can be fed into the command line <a href="https://github.com/wwood/singlem">SingleM</a> program.</p>
          <!-- <br /> -->

          <!-- <p>See a <a :href="'/otus/' + accession">visualisation</a></p> -->
        </div>
      </section>

      <section class="section">
        <div class="container is-large">
          <RunMetadata :mdata="metadata.metadata" :mdata_parsed="metadata.metadata_parsed" />
        </div>
      </section>
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

import { api_url, fetchRunMetadata, fetchRunCondensed } from '@/api'

export default {
  name: 'Run',
  title () {
    return `Run ${this.accession} - Sandpiper`
  },
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
    bioproject_url: function () {
      return 'https://www.ncbi.nlm.nih.gov/bioproject/' + this.metadata.metadata_parsed.bioproject
    },
    scholar_search_url: function () {
      // Unclear whether including accession helps. 
      return 'https://scholar.google.com/scholar?q=' + this.metadata.metadata_parsed.bioproject + ' OR ' + this.accession
    },
    getNumReads: function () {
      return Math.round(this.metadata.metadata_parsed.mbases / this.metadata.metadata_parsed.avgspotlen)
    },
    sunburst_tree: function () {
      return this.condensed_tree.condensed
    },
    sample_name_mature: function () {
      return this.metadata.metadata_parsed.sample_name
      // if (this.metadata.metadata_parsed.sample_name_sam !== null) {
      //   return this.metadata.metadata.sample_name_sam
      // } else {
      //   return this.metadata.metadata.sample_name
      // }
    },
    read_length_mature: function () {
      if (this.metadata.metadata_parsed.read_length_summary === null) {
        return ''
      } else {
        return '| ' + this.metadata.metadata_parsed.read_length_summary + ' '
      }      
    },
    full_profile_link: function () {
      return api_url() + '/otus/' + this.accession
    },
    publications: function () {
      return this.metadata.metadata.study_links.filter(function (link) {
        return (typeof link['database'] !== 'undefined')
      })
    },
    non_publication_study_links: function () {
      return this.metadata.metadata.study_links.filter(function (link) {
        return (typeof link['label'] !== 'undefined')
      })
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
    }
  },
  watch: {
    // call again the method if the route changes
    $route: 'fetchData'
  }
}
</script>
