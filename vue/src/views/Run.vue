<template>
  <div class="sunburst">
    <!-- <img alt="Vue logo" src="../assets/logo.png"> -->
    run
    <hr>
    acc: {{ condensed.sample_name }}
    <hr>
    <Sunburst :json_tree="condensed.condensed" />
    <hr>
  </div>
</template>

<script>
/* eslint-disable vue/no-unused-components */
import Sunburst from '@/components/Sunburst.vue'
import SampleJson from '@/sample.json'
/* eslint-disable no-unused-vars */
import { mapState } from 'vuex'

export default {
  name: 'Run',
  components: {
    Sunburst
  },
  computed: {
    condensed () {
      console.log('condensing')
      return this.$store.state.currentCondensed
    }
  },
  // computed: mapState({
  //   condensed: state => state.currentCondensed.condensed
  // }),
  beforeMount () {
    console.log('Run beforeMount: ' + this.$route.params.runId)
    this.$store.dispatch('loadCondensed', this.$route.params.runId)
    console.log('end of beforeMount' + this.$store)
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
