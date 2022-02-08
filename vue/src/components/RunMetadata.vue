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

// import DataTable from 'vue-data-tablee'

export default {
  name: 'RunMetadata',
  props: ['mdata'],
  components: {
    // DataTable
    // breadcrumbTrail,
    // highlightOnHover,
    // nodeInfoDisplayer,
    // sunburst,
    // popUpOnHover,
    // zoomOnClick
  },
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
    // phylogenyColor (d) {
    //   const order = d[0]
    //   const depth = d[1]
    //   const baseColors = ['#a6cee3', '#1f78b4', '#b2df8a', '#33a02c', '#fb9a99', '#e31a1c', '#fdbf6f', '#ff7f00', '#cab2d6', '#6a3d9a']

    //   const base = baseColors[order]
    //   const colorScale = scaleLinear()
    //     .domain([1, 12])
    //     .range([base, 'white'])

    //   return colorScale(depth)
    // },
    // phylogenyDataForColor (d) {
    //   return [d.order, d.depth]
    // }

    // myShowLabels (d) {
    //   console.log(d)
    //   return d.depth < 2
    // }
  },
  data () {
    return {
      medata: this.mdata
    }
  }
}
</script>
