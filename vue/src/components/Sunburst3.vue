<template>
<div>
  <!-- here: {{this.getdata()}} aye -->
  <!-- <svg class="sunburst">{{ sunburst(this.getdata()) }}</svg> -->
  <!-- {{ sunburst(this.getdata()) }} -->
  <!-- <svg id="sunburst3"><circle/></svg> -->
  <svg id="dataviz_area" class="sunburst" height=400></svg>
  </div>
</template>

<script>
// import { sunburstA } from '@/api/sunburst.js'
// import 'vue-d3-sunburst/dist/vue-d3-sunburst.css'

// import { scaleLinear } from 'd3-scale'
import * as d3 from 'd3'
import { scaleLinear } from 'd3-scale'

export default {
  name: 'Sunburst3',
  props: ['json_tree'],
  mounted () {
    this.sunburst(this.json_tree)
  },
  methods: {
    partition (sunburstData) {
      const root = d3.hierarchy(sunburstData)
        .sum(d => d.size)
        .sort((a, b) => b.order - a.order)
      return d3.partition()
        .size([2 * Math.PI, root.height + 1])(root)
    },
    sunburst (sunburstData) {
      // const color = function (s) {
      //   phylogenyColor(s)
      // } // self.phylogenyColor // d3.scaleOrdinal(d3.quantize(d3.interpolateRainbow, 30))
      const format = d3.format('.2f')
      const width = 600 // 932
      const radius = width / 18
      var arc = d3.arc()
        .startAngle(d => d.x0)
        .endAngle(d => d.x1)
        .padAngle(d => Math.min((d.x1 - d.x0) / 2, 0.005))
        .padRadius(radius * 1.5)
        .innerRadius(d => d.y0 * radius)
        .outerRadius(d => Math.max(d.y0 * radius, d.y1 * radius - 1))

      const root = this.partition(sunburstData)

      root.each(d => { d.current = d })

      // const svg = d3.create('svg')
      const svg = d3.select('#dataviz_area')
        .attr('viewBox', [0, 0, width, width])
        // .style('font', '10px')

      const g = svg.append('g')
        .attr('transform', `translate(${width / 2},${width / 2})`)

      const path = g.append('g')
        .selectAll('path')
        .data(root.descendants())
        .join('path')
        .attr('fill', d => { return this.phylogenyColor(d.data.order, d.data.condensed_depth) })
        .attr('fill-opacity', d => arcVisible(d.current) ? (d.children ? 0.6 : 0.4) : 0)
        .attr('pointer-events', d => arcVisible(d.current) ? 'auto' : 'none')

        .attr('d', d => arc(d.current))

      path.filter(d => d.children)
        .style('cursor', 'pointer')
        .on('click', clicked)
        .on('mouseover', function (_event, p) {
          path.filter(d => d.data.name === p.data.name)
            .attr('stroke', '#000')
            .attr('stroke-width', '2px')
            .attr('fill-opacity', 0.1)
        })
        .on('mouseout', function (_event, p) {
          path
            .attr('stroke', 'none')
            .attr('fill-opacity', d => arcVisible(d.current) ? (d.children ? 0.6 : 0.4) : 0)
        })

      path.append('title')
        .text(d => `${d.ancestors().map(d => d.data.name).reverse().join('; ')}\ncoverage: ${format(d.data.size)}\n`)

      const label = g.append('g')
        .attr('pointer-events', 'none')
        .attr('text-anchor', 'middle')
        .style('user-select', 'none')
        .selectAll('text')
        .data(root.descendants().slice())
        .join('text')
        .attr('dy', '0.35em')
        .attr('fill-opacity', d => +labelVisible(d.current))
        .attr('transform', d => labelTransform(d.current))
        .text(d => d.data.name)

      const parent = g.append('circle')
        .datum(root)
        .attr('r', radius)
        .attr('fill', 'none')
        .attr('pointer-events', 'all')
        .on('click', clicked)

      function clicked (_event, p) {
        parent.datum(root)

        root.each(d => {
          d.target = {
            x0: Math.max(0, Math.min(1, (d.x0 - p.x0) / (p.x1 - p.x0))) * 2 * Math.PI,
            x1: Math.max(0, Math.min(1, (d.x1 - p.x0) / (p.x1 - p.x0))) * 2 * Math.PI,
            y0: Math.max(0, d.y0 - p.depth),
            y1: Math.max(0, d.y1 - p.depth)
          }
        })

        const t = g.transition().duration(750)

        // Transition the data on all arcs, even the ones that aren’t visible,
        // so that if this transition is interrupted, entering arcs will start
        // the next transition from the desired position.
        path.transition(t)
          .tween('data', d => {
            const i = d3.interpolate(d.current, d.target)
            return t => { d.current = i(t) }
          })
          .filter(function (d) {
            return +this.getAttribute('fill-opacity') || arcVisible(d.target)
          })
          .attr('fill-opacity', d => arcVisible(d.target) ? (d.children ? 0.6 : 0.4) : 0)
          .attr('pointer-events', d => arcVisible(d.target) ? 'auto' : 'none')

          .attrTween('d', d => () => arc(d.current))

        label.filter(function (d) {
          return +this.getAttribute('fill-opacity') || labelVisible(d.target)
        }).transition(t)
          .attr('fill-opacity', d => +labelVisible(d.target))
          .attrTween('transform', d => () => labelTransform(d.current))
      }

      function arcVisible (d) {
        return true // d.y1 <= 3 && d.y0 >= 1 && d.x1 > d.x0
      }

      function labelVisible (d) {
        return (d.y1 - d.y0) * (d.x1 - d.x0) > 0.05
      }

      function labelTransform (d) {
        const x = (d.x0 + d.x1) / 2 * 180 / Math.PI
        const y = (d.y0 + d.y1) / 2 * radius
        return `rotate(${x - 90}) translate(${y},0) rotate(20) rotate(${x - 90 + 20 < 90 || x - 90 + 20 > 270 ? 0 : 180})`
      }

      return svg.node()
    },

    phylogenyColor (order, depth) {
      // console.log('colors in' + d[0] + ' : ' + d[1])
      // console.log(order, depth)
      // const order = d[0]
      // const depth = d[1]
      // const order = order
      // const depth = condensed_depth
      // console.log(order + '==' + depth)
      const baseColors = ['#a6cee3', '#1f78b4', '#b2df8a', '#33a02c', '#fb9a99', '#e31a1c', '#fdbf6f', '#ff7f00', '#cab2d6', '#6a3d9a']

      const base = baseColors[order]
      const colorScale = scaleLinear()
        .domain([1, 12])
        .range([base, 'white'])
      if (depth === 0) {
        return 'white'
      } else {
        return colorScale(depth)
      }
    }
  }
  // components: {
  //   breadcrumbTrail,
  //   highlightOnHover,
  //   nodeInfoDisplayer,
  //   sunburst,
  //   popUpOnHover,
  //   zoomOnClick
  // },
  // methods: {
  //   phylogenyColor (d) {
  //     const order = d[0]
  //     const depth = d[1]
  //     const baseColors = ['#a6cee3', '#1f78b4', '#b2df8a', '#33a02c', '#fb9a99', '#e31a1c', '#fdbf6f', '#ff7f00', '#cab2d6', '#6a3d9a']

  //     const base = baseColors[order]
  //     const colorScale = scaleLinear()
  //       .domain([1, 12])
  //       .range([base, 'white'])

  //     return colorScale(depth)
  //   },
  //   phylogenyDataForColor (d) {
  //     return [d.order, d.depth]
  //   }

  //   // myShowLabels (d) {
  //   //   console.log(d)
  //   //   return d.depth < 2
  //   // }
  // }
}

</script>
