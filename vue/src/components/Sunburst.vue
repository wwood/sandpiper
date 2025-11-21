<template>
  <sunburst :data="json_tree" :showLabels=true :max-label-text=null :centralCircleRelativeSize=15 :colorScale=phylogenyColor :getCategoryForColor=phylogenyDataForColor>

  <!-- Add behaviors -->
  <template slot-scope="{ on, actions }">
    <highlightOnHover v-bind="{ on, actions }"/>
    <zoomOnClick v-bind="{ on, actions }"/>
    <popUpOnHover v-bind="{ on, actions }"/>
  </template>

  <!-- Add information to be displayed on top the graph -->
  <nodeInfoDisplayer slot="top" slot-scope="{ nodes }" :current="nodes.mouseOver" :root="nodes.root" description="of microbial community" />

  <!-- Add bottom legend -->
  <breadcrumbTrail slot="legend" slot-scope="{ nodes, colorGetter, width }" :current="nodes.mouseOver" :root="nodes.root" :colorGetter="colorGetter" :from="nodes.clicked" :width="width" />

  <!-- Add pop-up -->
  <template slot="pop-up" slot-scope="{ data }">
      <div class="pop-up">{{data.name}}</div>
  </template>

  </sunburst>
</template>

<script>
import {
  breadcrumbTrail,
  highlightOnHover,
  nodeInfoDisplayer,
  popUpOnHover,
  sunburst,
  zoomOnClick
} from 'vue-d3-sunburst'
import 'vue-d3-sunburst/dist/vue-d3-sunburst.css'

import { scaleLinear } from 'd3-scale'

export default {
  name: 'Sunburst',
  props: ['json_tree'],
  components: {
    breadcrumbTrail,
    highlightOnHover,
    nodeInfoDisplayer,
    sunburst,
    popUpOnHover,
    zoomOnClick
  },
  methods: {
    phylogenyColor (d) {
      const order = d[0]
      const depth = d[1]
      const baseColors = ['#a6cee3', '#1f78b4', '#b2df8a', '#33a02c', '#fb9a99', '#e31a1c', '#fdbf6f', '#ff7f00', '#cab2d6', '#6a3d9a']

      const base = baseColors[order]
      const colorScale = scaleLinear()
        .domain([1, 12])
        .range([base, 'white'])

      return colorScale(depth)
    },
    phylogenyDataForColor (d) {
      return [d.order, d.depth]
    }

    // myShowLabels (d) {
    //   console.log(d)
    //   return d.depth < 2
    // }
  }
}
</script>
