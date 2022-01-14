<template>
  <sunburst :data="tree" :showLabels=true :max-label-text=null :centralCircleRelativeSize=15>

  <!-- Add behaviors -->
  <template slot-scope="{ on, actions }">
    <highlightOnHover v-bind="{ on, actions }"/>
    <zoomOnClick v-bind="{ on, actions }"/>
    <popUpOnHover v-bind="{ on, actions }"/>
  </template>

  <!-- Add information to be displayed on top the graph -->
  <nodeInfoDisplayer slot="top" slot-scope="{ nodes }" :current="nodes.mouseOver" :root="nodes.root" description="of mirobial community" />

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
  data () {
    return {
      tree: this.json_tree
      // tree: {
      //   name: 'flare',
      //   children: [
      //     {
      //       name: 'analytics',
      //       children: [
      //         {
      //           name: 'cluster',
      //           children: [
      //             { name: 'AgglomerativeCluster', size: 3938 },
      //             { name: 'CommunityStructure', size: 3812 },
      //             { name: 'HierarchicalCluster', size: 6714 },
      //             { name: 'MergeEdge', size: 743 }
      //           ]
      //         },
      //         {
      //           name: 'graph',
      //           children: [
      //             { name: 'BetweennessCentrality', size: 3534 },
      //             { name: 'LinkDistance', size: 5731 },
      //             { name: 'MaxFlowMinCut', size: 7840 },
      //             { name: 'ShortestPaths', size: 5914 },
      //             { name: 'SpanningTree', size: 3416 }
      //           ]
      //         },
      //         {
      //           name: 'optimization',
      //           children: [
      //             { name: 'AspectRatioBanker', size: 7074 }
      //           ]
      //         }
      //       ]
      //     }
      //   ]
      // }
    }
  }
}
</script>
