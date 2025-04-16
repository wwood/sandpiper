<template>
  <div class="columns">
    <div class="column is-three-quarters">
      <svg id="dataviz_area" class="sunburst" height=400 width=400></svg>
    </div>
    <div class="column sunburst-annotation">
      <svg class="sunburst-annotation" id="annotation_area" height=400 width=300></svg>
    </div>
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
  props: ['json_tree','known_species_fraction'],
  mounted () {
    this.sunburst(this.json_tree, this.known_species_fraction)
  },
  updated () {
    this.sunburst(this.json_tree, this.known_species_fraction)
  },
  // watch: {
  //   // call again the method if the route changes
  //   // $route: 'sunburst'
  //   load: function () {
  //     this.mounted()
  //   }
  // },
  methods: {
    partition (sunburstData) {
      const root = d3.hierarchy(sunburstData)
        .sum(d => d.size)
        .sort((a, b) => b.order - a.order)
      return d3.partition()
        .size([2 * Math.PI, root.height + 1])(root)
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

      const base = baseColors[order % baseColors.length]
      const colorScale = scaleLinear()
        .domain([1, 12])
        .range([base, 'white'])
      if (depth === 0) {
        return 'white'
      } else {
        return colorScale(depth)
      }
    },

    sunburst (sunburstData, known_species_fraction) {
      // const sunburstData = this.json_tree
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

      // clear SVG contents first
      d3.select('#dataviz_area > *').remove()
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

      path
        .style('cursor', 'pointer')
        .on('dblclick', doubleclicked)
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
        .text(d => `${d.ancestors().map(d => d.data.name).reverse().join(' ')}\ncoverage: ${format(d.sum(d => d.size).value)}\n`)

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
        .on('dblclick', doubleclicked)

      // Calculate total coverage amongst all lineages
      const overallCoverage = d3.hierarchy(sunburstData)
        .sum(function (d) { return d.size }).value


      // Known species_fraction
      var width_donut = 500
      var margin_donut = 40

      // The radius of the pieplot is half the width or half the height (smallest one). I subtract a bit of margin.
      var radius_donut = Math.min(width_donut, width_donut) / 2 - margin_donut

      const gpie = d3.select('#annotation_area').attr('viewBox', [0, 0, 600, 600]).append('g')
      gpie.append('text')
        .attr('x', 60)
        .attr('y', 550)
        .text(`known species fraction: ${round(known_species_fraction,0)}%`)
      var gpie_svg = gpie.append('svg')
        .attr('width', width_donut)
        .attr('height', width_donut)
        .append('g')
          .attr("transform", "translate(" + width_donut / 2 + "," + width_donut / 2 + ")")
      var pie = d3.pie()
        // Sort so that the known species slice is first going clockwise
        .value(function(d) {return d.value; }).sort((a) => {
          if (a.type === 'inc') {
            return -1;
          } else {
            return 1;
          }
        });
      var data_ready = pie([
        // hack here so that the key names are the values used for the stroke attr
        {"key": "2px", "type": 'inc', "colour": "#48c78e", "value": known_species_fraction}, 
        {"key": "0.5px", "type": 'not inc', "colour": "#ffffff", "value": 100 - known_species_fraction}])
      gpie_svg
        .selectAll('whatever')
        .data(data_ready)
        .enter()
        .append('path')
        .attr('d', d3.arc()
          .innerRadius(100)         // This is the size of the donut hole
          .outerRadius(radius_donut)
        )
        .attr('fill', function(d){ return d.data.colour })
        .attr("stroke", "black")
        .style("stroke-width", function(d){ return d.data.key })
        .style("opacity", 1)
      // console.log('species_fraction: ' + known_species_fraction)


      function clicked (_event, p) {
        // clear any content currently there
        d3.select('#annotation_area > *').remove()

        // Annotate the annotation_area with name, taxonomy and coverage info
        const svg = d3.select('#annotation_area')
          .attr('viewBox', [0, 0, 600, 600])
        const g = svg.append('g')
        const linewidth = 50

        // Taxonomy is all parents in order except the root
        var current = p
        var taxonomy = []
        while (current.parent) {
          taxonomy.push(current.data.name)
          current = current.parent
        }
        taxonomy = taxonomy.reverse()
        for (var i = 0; i < taxonomy.length; i++) {
          // g.append('text')
          //   .attr('x', 0)
          //   .attr('y', linewidth * (i + 2))
          //   .text(`${taxonomy[taxonomy.length - i - 1]}`)
          const taxonPrefix = ['d__', 'p__', 'c__', 'o__', 'f__', 'g__', 's__'][i]
          const taxonLink = '/taxonomy/' + taxonPrefix + taxonomy[i]
          // g.append('svg:a')
          //   .attr('xlink:href', taxonLink)
          //   .append('svg')
          //   .attr('x', 0)
          //   .attr('y', linewidth * (i + 2))
          //   .attr('font-family', 'FontAwesome 5 Free')
          //   .attr('font-size', '5em') // function (d) { return d.size + 'em' })
          //   // .text('\uf871')
          //   .text('&#xf871')

          // g.append('svg:a')
          //   .attr('xlink:href', taxonLink)
          //   .append('text')
          //   .attr('x', 0)
          //   .attr('y', linewidth * (i + 2))
          //   .attr('font-family', 'FontAwesome 5 Free')
          //   .attr('font-size', '5em') // function (d) { return d.size + 'em' })
          //   // .text('\uf871')
          //   .text('&#xf871')
          // ${taxonPrefix[i][0]}: 
          g.append('svg')
            .append('text')
            .attr('x', 50) //75
            .attr('y', linewidth * (i + 2))
            .text(`${taxonPrefix[0]}: `)
          g.append('svg:a')
            .attr('xlink:href', taxonLink)
            .append('text')
            .attr('x', 90) //75
            .attr('y', linewidth * (i + 2))
            .attr('class', 'svg-link')
            .text(`${taxonomy[i]}`)
        }
        // At most 6 levels of depth I think

        // calculate total coverage as size of node and descendents
        var totalCoverage = p.sum(d => d.size).value
        g.append('text')
          .attr('x', 0)
          .attr('y', 10 * linewidth)
          .text(`coverage: ${round(totalCoverage, 2)}`)

        g.append('text')
          .attr('x', 0)
          .attr('y', 12 * linewidth)
          .text(`relative abundance: ${round(totalCoverage / overallCoverage * 100, 2)} %`)
      }

      function round (value, precision) {
        var multiplier = Math.pow(10, precision || 0)
        return Math.round(value * multiplier) / multiplier
      }

      function doubleclicked (_event, p) {
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
    }
  }
}

</script>
