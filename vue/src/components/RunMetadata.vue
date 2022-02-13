<template>
<div>
<div class="container">
<section>
      <h3 class="title">General metadata</h3>
      <b-table :data="gatherMetadata ()" :columns="generalMetadataColumns()" :striped="true" />
</section>
</div>
&nbsp;
<div class="container">
<section>
      <h3 class="title">BioSample metadata</h3>
      <b-table :data="mdata.biosample_attributes" :columns="column_definition()" :striped="true" />
</section>
</div>
</div>
</template>

<script>

import 'vue-data-tablee/dist/vue-data-tablee.css'

export default {
  name: 'RunMetadata',
  props: ['mdata'],
  methods: {
    // Data to be put in the general metadata
    gatherMetadata () {
      const toReturn = []
      Object.keys(this.mdata).forEach(key => {
        // console.log('key: ' + key)
        const v = this.mdata[key]
        if (key !== 'biosample_attributes' && v !== null) {
          toReturn.push({
            k: key,
            value: v
          })
        }
      })
      return toReturn
    },
    generalMetadataColumns () {
      return [{ label: 'attribute', field: 'k' }, { label: 'value', field: 'value' }]
    },
    column_definition () {
      return [{ label: 'attribute', field: 'k', align: 'center' }, { label: 'value', field: 'v' }]
    }
  },
  data () {
    return {
      medata: this.mdata
    }
  }
}
</script>
