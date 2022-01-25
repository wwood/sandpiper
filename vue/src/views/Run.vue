<template>
  <div class="sunburst">
    <!-- <img alt="Vue logo" src="../assets/logo.png"> -->
    run
    <hr>
    <!-- acc: FIXME {{ accession }} -->
    <hr>
    <Sunburst :json_tree="condensed" />
    <!-- <Sunburst :json_tree="getSampleJson()" /> -->
  </div>
</template>

<script>
import Sunburst from '@/components/Sunburst.vue'
import SampleJson from '@/sample.json'
import { mapState } from 'vuex'

export default {
  name: 'Run',
  components: {
    Sunburst
  },
  // computed: {
  //   accession () {
  //     return this.$route.params.runId
  //   }
  // },
  // computed: mapState(['currentCondensed']),
  // computed: {
  //   currentCondensed () {
  //     return store.state.currentCondensed
  //   }
  // },
  computed: mapState({
    condensed: state => state.currentCondensed
  }),
  beforeMount () {
    this.$store.dispatch('loadCondensed', this.$route.params.runId)
  },
  methods: {
    getSampleJson () {
      console.log('getting sample json')
      // Next, make this dynamic by querying the database
      return SampleJson
    }
  }
}
</script>
