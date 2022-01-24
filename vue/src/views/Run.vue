<template>
  <div class="sunburst">
    <!-- <img alt="Vue logo" src="../assets/logo.png"> -->
    run
    <hr>
    <!-- acc: FIXME {{ accession }} -->
    <hr>
    <Sunburst :json_tree="condensed" />
  </div>
</template>

<script>
import Sunburst from '@/components/Sunburst.vue'
// import SampleJson from '@/sample.json'
import mapState from 'vuex'

export default {
  name: 'Run',
  components: {
    Sunburst
  },
  computed: mapState({
    condensed: state => state.currentCondensed
  //   accession () {
  //     return this.$route.params.runId
  //   }
  // },
  }),
  beforeMount () {
    this.$store.dispatch('setCondensed', this.$route.params.runId)
  },
  // methods: {
  //   getSampleJson () {
  //     console.log('getting sample json')
  //     // Next, make this dynamic by querying the database
  //     return SampleJson
  //   }
  // }
}
</script>
