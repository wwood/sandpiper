<template>
  <div>
    <section class="section">
    <div class="container">
      <h1 class="title">{{ condensed.sample_name }}</h1>

      <p class="subtitle">
        {{ metadata.metadata.organism }} ({{ metadata.metadata.librarysource.toLowerCase() }}) | {{ metadata.metadata.sample_name_sam }}
      </p>

      <div>
        {{ metadata.metadata.mbases / 1000}} Gbp | {{ getNumReads() }} million reads | {{ metadata.metadata.avgspotlen }} bp average read length | {{ metadata.metadata.instrument }}
      </div>

      <div>
        NCBI: <a :href="bioproject_url()">{{ bioproject_id() }}</a> | <a :href="run_url()">{{ condensed.sample_name }}</a>
      </div>

    </div>
    </section>

    <section>
      <div class="container is-large">
        <h3 class="title">Condensed profile</h3>

        <div class="sunburst">
          <template v-if="condensed != null">
            <Sunburst :json_tree="condensed.condensed" />
          </template>
        </div>
      </div>
    </section>

    <RunMetadata :mdata="metadata.metadata" />
  </div>
</template>

<script>

/* eslint-disable vue/no-unused-components */
import Sunburst from '@/components/Sunburst.vue'
import RunMetadata from '@/components/RunMetadata.vue'

export default {
  name: 'Run',
  components: {
    Sunburst, RunMetadata
  },
  computed: {
    condensed () {
      return this.$store.state.currentCondensed
    },
    metadata () {
      return this.$store.state.currentMetadata
    }
  },
  methods: {
    getNumReads () {
      return Math.round(this.metadata.metadata.mbases / this.metadata.metadata.avgspotlen)
    },
    bioproject_id () {
      return this.metadata.metadata.bioproject
    },
    bioproject_url () {
      const link = 'https://www.ncbi.nlm.nih.gov/bioproject/?term=' + this.metadata.metadata.bioproject
      return link
    },
    run_url () {
      const link = 'https://www.ncbi.nlm.nih.gov/sra?term=' + this.metadata.metadata.acc
      return link
    }
  },
  beforeMount () {
    this.$store.dispatch('loadCondensed', this.$route.params.runId)
    this.$store.dispatch('loadMetadata', this.$route.params.runId)
  }
}
</script>
