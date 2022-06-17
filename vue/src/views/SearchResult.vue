<template>
  <section class="section">
    <div v-if="search_result !== null" class="container">
      <section class="section">
        <!-- <h1 class="title">Search results for {{ taxonomy }}</h1> -->
        <h1 class="title" style="text-align: center;">
          The {{ taxonomy_level }}
          <span v-if="taxonomy_level==='species' || taxonomy_level==='genus'">
            <i>{{ taxon_name }}</i>
          </span>
          <span v-else>{{ taxon_name }}</span>
          </h1>
        <p style="text-align: center;">{{ lineage.join('; ') }}</p>
      </section>

      <section class="section">
        <nav class="level">
          <div class="level-item has-text-centered">
            <div class="level-item">
              <div>
                <a href="#matching-samples">
                  <p class="heading">Matching Samples</p>
                  <p class="title"> {{ total_num_results.toLocaleString("en-US") }}</p>
                </a>
                <p>runs total</p>
              </div>
            </div>
          </div>
          <div class="level-item has-text-centered">
            <div class="level-item">
              <div>
                <a href="#host-association-overview">
                  <p class="heading">Host-association</p>
                  <p class="title"> {{ Math.round((num_host_runs/(num_host_runs+num_ecological_runs)*100)) }}%</p>
                </a>
                <p>of runs are host-associated</p>
              </div>
            </div>
          </div>
          <div class="level-item has-text-centered">
            <div class="level-item">
              <div>
                <a href="#geographic-distribution">
                  <p class="heading">Geographic Distribution</p>
                  <p class="title" v-if="num_lat_lon_runs < 1000">{{ num_lat_lon_runs.toLocaleString("en-US") }}</p>
                  <p class="title" v-else>1000+</p>
                </a>
                <p>runs with >1% relative abundance and lat/lon.</p>
              </div>
            </div>
          </div>
        </nav>
      </section>

      <section class="section" id="geographic-distribution">
        <div class="section" v-if="this.lat_lons !== null">
          <h2 class="subtitle is-2 bd-anchor-title">
            <a class="bd-anchor-link" href="#geographic-distribution"># </a>
            <span class="bd-anchor-name">Geographic distribution</span>
          </h2>
          <!-- <div class="section"> -->
            <div v-if="this.num_lat_lon_runs < 1000">
              {{ this.num_lat_lon_runs.toLocaleString("en-US") }} runs have relative abundance > 1% and associated latitude/longitude metadata.
            </div>
            <div v-else>
              1,000+ runs have relative abundance > 1% and associated latitude/longitude metadata.
            </div>
            <br /><p>{{ (total_num_results - num_lat_lon_runs).toLocaleString("en-US") }} other runs are not shown on this map.</p><br />
          <!-- </div> -->
          <l-map style="height: 900px" :zoom="zoom" :center="center">
            <l-tile-layer :url="url" :attribution="attribution" />
            <l-marker v-for="markerLatLng in this.lat_lons" v-bind:key="markerLatLng[0]" :lat-lng="markerLatLng['lat_lon']">
              <l-popup :content="html_for_map_popup(markerLatLng)" :options="{ interactive: true }">
              </l-popup>
            </l-marker>
          </l-map>
        </div>
      </section>

      <section class="section" id="matching-samples">
        <h2 class="subtitle is-2 bd-anchor-title">
          <a class="bd-anchor-link" href="#matching-samples"># </a>
          <span class="bd-anchor-name">Matching samples</span>
        </h2>
        <b-button tag="a" type="is-info" :href="csv_link()">Download CSV</b-button>
        <b-table
          :data="search_result['condensed_profiles']"
          :loading="loading"
          :striped="true"
          :sort-icon="'arrow-up'"
          :default-sort="this.sortField"
          :default-sort-direction="this.sortDirection"
          paginated
          :current-page="this.page"
          :per-page="this.pageSize"
          pagination-simple
          backend-pagination
          backend-sorting
          :total="total_num_results"
          @page-change="onPageChange"
          @sort="onSort">

          <b-table-column field='sample_name' label='Run' v-slot="props">
            <a :href="'/run/' + props.row.sample_acc">{{ props.row.sample_acc }}</a>
          </b-table-column>

          <b-table-column field='organism' label='Environment' v-slot="props" sortable>
            {{ props.row.organism }}
          </b-table-column>

          <b-table-column field='collection_year' label='Year' v-slot="props" centered sortable>
            {{ props.row.collection_year }}
          </b-table-column>

          <b-table-column field='relative_abundance' label='Relative abundance (%)' v-slot="props" centered sortable>
            {{ props.row.relative_abundance }}
          </b-table-column>

          <b-table-column field='coverage' label='Coverage' v-slot="props" centered sortable>
            {{ props.row.coverage }}
          </b-table-column>
        </b-table>
      </section>
    </div>

    <div v-else>
      <div v-if="error_message !== null">
        <section class="section container">
          <b-message 
            title="Error" 
            type="is-warning" 
            :closable="false"
            has-icon>
            <p>{{ error_message }}</p>
          </b-message>
        </section>
      </div>

      <div v-else>
        <section class="section container">
          Searching ..
        </section>
      </div>
    </div>

  </section>
</template>

<script>
import { api_url, fetchGlobalDataByTaxonomy, fetchRunsByTaxonomy } from '@/api'

// If you need to reference 'L', such as in 'L.icon', then be sure to
// explicitly import 'leaflet' into your component
// import L from 'leaflet'
import { LMap, LTileLayer, LMarker, LPopup } from 'vue2-leaflet'

// Make the marker appear https://vue2-leaflet.netlify.app/quickstart/#marker-icons-are-missing
import { Icon, latLng } from 'leaflet'

delete Icon.Default.prototype._getIconUrl
Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png')
})

export default {
  name: 'SearchResults',
  props: ['taxonomy'],
  components: {
    LMap,
    LTileLayer,
    LMarker,
    LPopup
  },
  data: function () {
    return {
      loading: true,
      search_result: null,
      taxon_name: null,
      lineage: null,
      sortIcon: 'arrow-up',
      total_num_results: null,
      page: 1,
      pageSize: 100,
      sortField: 'relative_abundance',
      sortDirection: 'desc',
      error_message: null,

      lat_lons: null,
      num_lat_lon_runs: null,
      url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      attribution:
        '&copy; <a target="_blank" href="http://osm.org/copyright">OpenStreetMap</a> contributors',
      center: latLng(0, 0),
      zoom: 1.5
    }
  },
  created () {
    // fetch the data when the view is created and the data is
    // already being observed
    this.fetchGlobalData()
  },
  methods: {
    fetchGlobalData () {
      fetchGlobalDataByTaxonomy(this.taxonomy)
        .then(response => {
          if (response.data.total_num_results > 0) {
            this.taxon_name = response.data.taxon_name
            this.lineage = response.data.lineage
            this.taxonomy_level = response.data.taxonomy_level
            this.total_num_results = response.data.total_num_results
            this.lat_lons = response.data.lat_lons
            this.num_lat_lon_runs = response.data.num_lat_lon_runs
            this.num_host_runs = response.data.num_host_runs
            this.num_ecological_runs = response.data.num_ecological_runs
          } else {
            this.error_message = response.data.taxon
          }
        })
      this.fetchData() // call here so that this and the run data are loaded by the watch in a single function
    },
    fetchData () {
      this.loading = true
      this.search_result = null

      fetchRunsByTaxonomy(this.taxonomy, this.page, this.sortField, this.sortDirection, this.pageSize)
        .then(response => {
          this.search_result = response.data.results
          this.loading = false
        })
    },
    onPageChange (page) {
      this.page = page
      this.fetchData()
    },
    onSort (field, direction) {
      this.sortField = field
      this.sortDirection = direction
      this.fetchData()
    },
    numericColumnTdAttrs (_row, _column) {
      return {
        style: 'text-align: center;'
      }
    },
    html_for_map_popup (markerLatLng) {
      let toReturn = ''
      Object.entries(markerLatLng.samples).forEach((description_samples) => {
        toReturn += '<p>' + description_samples[0] + '</p>'
        toReturn += '<ul>'
        description_samples[1].forEach((sample) => {
          toReturn += '<li><a href="/run/' + sample+ '">' + sample + '</a></li>'
        })
        toReturn += '</ul>'
      })
      return toReturn
    },
    csv_link () {
      return api_url() + '/taxonomy_search_csv/' + this.taxonomy
    }
  },
  watch: {
    // call again the method if the route changes
    $route: 'fetchGlobalData'
  }
}
</script>
