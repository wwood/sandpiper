<template>
  <div>
    <div v-if="metadata !== null">
      <section class="section">
        <div class="container" v-if="metadata !== null">
          <h1 class="title">Runs related to {{ model_bioproject }}</h1>

          <div class="has-text-justified">
            <br />
            <p>{{ metadata.study_abstract }}</p>
          </div><br />

          <b-table
            :data="metadata.projects"
            :striped="true" 
            :sort-icon="'arrow-up'">

            <b-table-column field="acc" label="Run" v-slot="props" width="300" sortable>
              <b><router-link :to="{ name: 'Run', params: { accession: props.row.acc }}">{{ props.row.acc }}</router-link></b>
            </b-table-column>
            <b-table-column field="sample_name" label="Sample" v-slot="props" sortable centered>
              {{ props.row.sample_name }}
            </b-table-column>
            <b-table-column field="library_name" label="Library" v-slot="props" sortable centered>
              {{ props.row.library_name }}
            </b-table-column>
            <b-table-column field="experiment_title" label="Experiment" v-slot="props" sortable centered>
              {{ props.row.experiment_title }}
            </b-table-column>
            <b-table-column field="gbp" label="Gbp" v-slot="props" sortable numeric centered>
              {{ props.row.gbp }}
            </b-table-column>
          </b-table>

          <!-- <div>
            {{ metadata.metadata_parsed.organism }} | {{
            metadata.metadata_parsed.mbases / 1000}} Gbp | {{ getNumReads }} million
            reads {{ read_length_mature }}|
            {{ metadata.metadata_parsed.instrument }} | Released {{
            metadata.metadata_parsed.release_month }}
            <br />
            NCBI: <a :href="bioproject_url">{{ metadata.metadata_parsed.bioproject }}</a> | <a :href="'http://www.ncbi.nlm.nih.gov/sra?term=' + accession">{{ accession }}</a>
            <br />
          </div> -->

          <!-- <div>
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
          </div> -->

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

import { fetchProjectMetadata } from '@/api'

export default {
  name: 'Project',
  title () {
    return `Project overview - Sandpiper` // FIXME
  },
  data: function () {
    return {
      model_bioproject: null,
      metadata: null,
      error_message: null
    }
  },
  // props: ['accession'],
  // components: {
  //   Sunburst3,
  //   RunMetadata
  // },
  computed: {
    // bioproject_url: function () {
    //   return 'https://www.ncbi.nlm.nih.gov/bioproject/' + this.metadata.metadata_parsed.bioproject
    // },
    // scholar_search_url: function () {
    //   // Unclear whether including accession helps. 
    //   return 'https://scholar.google.com/scholar?q=' + this.metadata.metadata_parsed.bioproject + ' OR ' + this.accession
    // },
    // getNumReads: function () {
    //   return Math.round(this.metadata.metadata_parsed.mbases / this.metadata.metadata_parsed.avgspotlen)
    // },
    // sunburst_tree: function () {
    //   return this.condensed_tree.condensed
    // },
    // sample_name_mature: function () {
    //   return this.metadata.metadata_parsed.sample_name
    //   // if (this.metadata.metadata_parsed.sample_name_sam !== null) {
    //   //   return this.metadata.metadata.sample_name_sam
    //   // } else {
    //   //   return this.metadata.metadata.sample_name
    //   // }
    // },
    // read_length_mature: function () {
    //   if (this.metadata.metadata_parsed.read_length_summary === null) {
    //     return ''
    //   } else {
    //     return '| ' + this.metadata.metadata_parsed.read_length_summary + ' '
    //   }      
    // },
    // full_profile_link: function () {
    //   return api_url() + '/otus/' + this.accession
    // },
    // publications: function () {
    //   return this.metadata.metadata.study_links.filter(function (link) {
    //     return (typeof link['database'] !== 'undefined')
    //   })
    // },
    // non_publication_study_links: function () {
    //   return this.metadata.metadata.study_links.filter(function (link) {
    //     return (typeof link['label'] !== 'undefined')
    //   })
    // }
  },
  created () {
    // fetch the data when the view is created and the data is
    // already being observed
    this.fetchData()
  },
  methods: {
    fetchData () {
      const model_bioproject = this.$route.query.model_bioproject
      this.model_bioproject = model_bioproject

      fetchProjectMetadata(model_bioproject)
        .then(response => {
          if (response.data.error !== undefined) {
            this.error_message = response.data.error
          } else {
            this.metadata = response.data
          }
        })
    },
  },
  watch: {
    // call again the method if the route changes
    $route: 'fetchData'
  }
}
</script>
