<template>
  <div class="sunburst-block">
    <div class="sunburst-search">
      <b-field>
        <b-input
          v-model="search_query"
          type="search"
          icon="magnify"
          placeholder="Highlight taxa e.g. Bacteroidota or p__Bacillota" />
      </b-field>
      <p class="help">{{ search_help }}</p>
    </div>

    <div class="columns is-centered">
      <div class="column is-two-thirds">
        <svg id="dataviz_area" class="sunburst" viewBox="0 0 600 600" preserveAspectRatio="xMidYMid meet"></svg>
      </div>
      <div class="column">
        <svg id="annotation_area" class="sunburst-annotation" viewBox="0 0 600 600" preserveAspectRatio="xMidYMid meet"></svg>
      </div>
    </div>
  </div>
</template>

<script>
// import { sunburstA } from '@/api/sunburst.js'
// import 'vue-d3-sunburst/dist/vue-d3-sunburst.css'

// import { scaleLinear } from 'd3-scale'
import * as d3 from 'd3'
import { scaleLinear } from 'd3-scale'

// Taxon names arrive from the API with their rank prefix stripped off, so the
// rank of a node is only recoverable from its depth in the condensed tree
// (the root is 0). These maps let a search term like "p__Bacillota" be
// restricted to the phylum ring.
const RANK_DEPTHS = { d: 1, p: 2, c: 3, o: 4, f: 5, g: 6, s: 7 }
const RANK_NAMES = {
  1: 'domain', 2: 'phylum', 3: 'class', 4: 'order', 5: 'family', 6: 'genus', 7: 'species'
}
// Short search terms match nearly everything, which highlights the whole
// sunburst and tells the user nothing, so require a few letters first.
const MIN_SEARCH_LETTERS = 4

export default {
  name: 'Sunburst3',
  props: ['json_tree', 'known_species_fraction'],
  data () {
    return {
      search_query: '',
      match_count: 0
    }
  },
  created () {
    // d3 selections held outside of data() so that Vue does not wrap the DOM
    // nodes they hold in reactive proxies.
    this.path_selection = null
    this.label_selection = null
    this.redraw_pending = false
  },
  mounted () {
    this.sunburst(this.json_tree, this.known_species_fraction)
  },
  computed: {
    // Split a query such as "p__Bacillota" into the rank it restricts to and
    // the text to match, and decide whether it is long enough to act on.
    parsed_search () {
      const raw = (this.search_query || '').trim()
      if (raw === '') {
        return { state: 'empty', rank: null, term: '' }
      }
      const prefix_match = /^([dpcofgs])__(.*)$/i.exec(raw)
      let rank = null
      let term = raw
      if (prefix_match !== null) {
        rank = RANK_DEPTHS[prefix_match[1].toLowerCase()]
        term = prefix_match[2]
      }
      term = term.trim()
      // Count letters/digits only, so "p__ " or "e. " do not count as a search
      const letters = term.replace(/[^\p{L}\p{N}]/gu, '')
      if (letters.length < MIN_SEARCH_LETTERS) {
        return { state: 'too_short', rank: rank, term: term }
      }
      return { state: 'ready', rank: rank, term: term.toLowerCase() }
    },
    search_help () {
      const query = this.parsed_search
      if (query.state === 'empty') {
        return `Type at least ${MIN_SEARCH_LETTERS} letters to highlight matching parts of the profile. Rank prefixes are respected, so p__Bacillota only matches phyla.`
      }
      if (query.state === 'too_short') {
        return `Type at least ${MIN_SEARCH_LETTERS} letters to highlight matching taxa.`
      }
      const at_rank = query.rank === null ? '' : ` at ${RANK_NAMES[query.rank]} level`
      if (this.match_count === 0) {
        return `No taxa${at_rank} in this profile match "${query.term}".`
      }
      if (this.match_count === 1) {
        return `1 taxon${at_rank} highlighted.`
      }
      return `${this.match_count} taxa${at_rank} highlighted.`
    }
  },
  watch: {
    // Redraw only when the profile being shown actually changes. Redrawing on
    // every component update would throw away the zoom state (and the arcs)
    // each time the search box is typed in.
    json_tree: 'redraw',
    known_species_fraction: 'redraw',
    search_query () {
      this.apply_highlight()
    }
  },
  methods: {
    // Both watched props change together when the taxonomy database is
    // switched, so coalesce them into a single redraw.
    redraw () {
      if (this.redraw_pending) {
        return
      }
      this.redraw_pending = true
      this.$nextTick(() => {
        this.redraw_pending = false
        this.sunburst(this.json_tree, this.known_species_fraction)
      })
    },

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

    // The opacity an arc has when no search is in effect.
    base_opacity (d) {
      return d.children ? 0.6 : 0.4
    },

    node_matches (d, query) {
      if (query.state !== 'ready') {
        return false
      }
      const name = d.data.name
      if (!name) {
        return false
      }
      if (query.rank !== null && d.data.condensed_depth !== query.rank) {
        return false
      }
      return name.toLowerCase().includes(query.term)
    },

    // Restyle the arcs (and their labels) to reflect the current search. Also
    // used to restore the resting appearance after a mouseout or a zoom.
    apply_highlight () {
      const path = this.path_selection
      const label = this.label_selection
      if (path === null) {
        return
      }
      const query = this.parsed_search

      if (query.state !== 'ready') {
        this.match_count = 0
        path
          .attr('stroke', 'none')
          .attr('stroke-width', null)
          .attr('fill-opacity', d => this.base_opacity(d))
        if (label !== null) {
          label.attr('font-weight', null)
        }
        return
      }

      let matches = 0
      path.each(d => { if (this.node_matches(d, query)) { matches++ } })
      this.match_count = matches

      path
        .attr('stroke', d => this.node_matches(d, query) ? '#000' : 'none')
        .attr('stroke-width', d => this.node_matches(d, query) ? '1.5px' : null)
        .attr('fill-opacity', d => this.node_matches(d, query) ? 0.95 : 0.1)
      if (label !== null) {
        label.attr('font-weight', d => this.node_matches(d, query) ? 'bold' : null)
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
      d3.selectAll('#dataviz_area > *').remove()
      d3.selectAll('#annotation_area > *').remove()
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
        .attr('fill-opacity', d => arcVisible(d.current) ? this.base_opacity(d) : 0)
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
        // Restore whatever the resting appearance is - which is the search
        // highlighting when a search is in effect, and the plain colouring
        // otherwise.
        .on('mouseout', () => this.apply_highlight())

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

      this.path_selection = path
      this.label_selection = label

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
        .attr('x', 30)
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

      // Re-apply any search highlighting, since the arcs have just been redrawn
      this.apply_highlight()

      function clicked (_event, p) {
        // clear any content currently there
        d3.selectAll('#annotation_area > *').remove()

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
          const taxonPrefix = ['d__', 'p__', 'c__', 'o__', 'f__', 'g__', 's__'][i]
          const taxonLink = '/taxonomy/' + taxonPrefix + taxonomy[i]
          g.append('svg')
            .append('text')
            .attr('x', 10)
            .attr('y', linewidth * (i + 1))
            .text(`${taxonPrefix[0]}: `)
          g.append('svg:a')
            .attr('xlink:href', taxonLink)
            .append('text')
            .attr('x', 50)
            .attr('y', linewidth * (i + 1))
            .attr('class', 'svg-link')
            .text(`${taxonomy[i]}`)
        }
        // At most 7 levels of depth, so the lines above end at y=350 and the
        // summary below must stay inside the 600 unit high viewBox.

        // calculate total coverage as size of node and descendents
        var totalCoverage = p.sum(d => d.size).value
        g.append('text')
          .attr('x', 10)
          .attr('y', 9 * linewidth)
          .text(`coverage: ${round(totalCoverage, 2)}`)

        g.append('text')
          .attr('x', 10)
          .attr('y', 10.5 * linewidth)
          .text(`relative abundance: ${round(totalCoverage / overallCoverage * 100, 2)} %`)
      }

      function round (value, precision) {
        var multiplier = Math.pow(10, precision || 0)
        return Math.round(value * multiplier) / multiplier
      }

      const reapply_highlight = () => this.apply_highlight()

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

        // The zoom transition rewrites fill-opacity, so put the search
        // highlighting back once it has finished.
        t.end().then(reapply_highlight, () => {})
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
