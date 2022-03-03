<template>
  <div>
    <section class="section container" v-if="total_num_results !== null">
      Found {{ total_num_results.toLocaleString("en-US") }} runs containing "<i>{{ taxonomy }}</i>"
    </section>

    <section class="section container" v-if="search_result !== null">
      <l-map style="height: 700px" :zoom="zoom" v-if="this.lat_lons !== null">
        <l-tile-layer :url="url" :attribution="attribution" />
          <l-marker v-for="markerLatLng in this.lat_lons" v-bind:key="markerLatLng[0]" :lat-lng="markerLatLng['lat_lon']">
            <l-popup :content="html_for_map_popup(markerLatLng)" :options="{ interactive: true }">
            </l-popup>
          </l-marker>
      </l-map>

      <div class="section">
        <h2 class="title is-4">Matching samples</h2>
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
            <a :href="'/run/' + props.row.sample_name">{{ props.row.sample_name }}</a>
          </b-table-column>

          <b-table-column field='relative_abundance' label='Relative abundance (%)' v-slot="props" centered sortable>
            {{ props.row.relative_abundance }}
          </b-table-column>

          <b-table-column field='coverage' label='Coverage' v-slot="props" centered sortable>
            {{ props.row.coverage }}
          </b-table-column>
        </b-table>
      </div>
    </section>
    <section class="section container" v-else>
      Searching ..
    </section>
  </div>
</template>

<script>
import { fetchGlobalDataByTaxonomy, fetchRunsByTaxonomy } from '@/api'

// If you need to reference 'L', such as in 'L.icon', then be sure to
// explicitly import 'leaflet' into your component
// import L from 'leaflet'
import { LMap, LTileLayer, LMarker, LPopup } from 'vue2-leaflet'

// Make the marker appear https://vue2-leaflet.netlify.app/quickstart/#marker-icons-are-missing
import { Icon } from 'leaflet'
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
      taxon: null,
      sortIcon: 'arrow-up',
      total_num_results: null,
      page: 1,
      pageSize: 100,
      sortField: 'relative_abundance',
      sortDirection: 'desc',

      lat_lons: null,
      url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      attribution:
        '&copy; <a target="_blank" href="http://osm.org/copyright">OpenStreetMap</a> contributors',
      zoom: 2
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
          this.taxon = response.data.taxon
          this.total_num_results = response.data.total_num_results
          this.lat_lons = response.data.lat_lons
          console.log('finished fetching global data')
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
      markerLatLng.sample_names.forEach((sample) => {
        // if (toReturn !== '') {
        //   toReturn += '<br>'
        // }
        toReturn += '<a href="/run/' + sample + '">' + sample + '</a><br>'
      })
      return toReturn
    }
  },
  watch: {
    // call again the method if the route changes
    $route: 'fetchGlobalData'
  }
}
</script>
