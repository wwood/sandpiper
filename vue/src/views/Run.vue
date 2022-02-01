<template>
  <div class="sunburst">
    <!-- <img alt="Vue logo" src="../assets/logo.png"> -->
    run
    <hr>
    acc: {{ condensed.sample_name }}
    <hr>
    <template v-if="condensed != null">
      <Sunburst :json_tree="condensed.condensed" />
    </template>
    <hr>
  </div>
</template>

<script>
import Sunburst from '@/components/Sunburst.vue'

export default {
  name: 'Run',
  components: {
    Sunburst
  },
  computed: {
    condensed () {
      return this.$store.state.currentCondensed
    }
  },
  beforeMount () {
    this.$store.dispatch('loadCondensed', this.$route.params.runId)
  }
}
</script>
