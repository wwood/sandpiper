<template>
  <section class="section container" v-if="search_result !== null">
    <div v-if="('condensed_profiles' in search_result)">
      Found {{ search_result['condensed_profiles'].length }} runs containing "<i>{{ taxonomy }}</i>"

      <l-map style="height: 700px" :zoom="zoom">
        <l-tile-layer :url="url" :attribution="attribution" />
          <l-marker v-for="markerLatLng in search_result['lat_lons']" v-bind:key='markerLatLng[0]' :lat-lng="markerLatLng['lat_lon']">
            <l-popup :content="'<a href=\'/run/' + markerLatLng['sample_name'] + '\'><b>' + markerLatLng['sample_name'] + '</b></a>'" :options="{ interactive: true }">
            </l-popup>
          </l-marker>
      </l-map>

      <div class="section">
        <h2 class="title is-4">Matching samples</h2>
        <b-table :data="search_result['condensed_profiles']" :striped="true" :sort-icon="'arrow-up'" default-sort="relative_abundance" :default-sort-direction="'desc'">

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
    </div>
    <div v-else>
      {{ search_result['taxon'] }}
    </div>
  </section>
  <section class="section container" v-else>
    Searching ..
  </section>
</template>

<script>
import { fetchRunsByTaxonomy } from '@/api'

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
      search_result: null,
      sortIcon: 'arrow-up',
      url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      attribution:
        '&copy; <a target="_blank" href="http://osm.org/copyright">OpenStreetMap</a> contributors',
      zoom: 2
    }
  },
  created () {
    // fetch the data when the view is created and the data is
    // already being observed
    this.fetchData()
  },
  methods: {
    fetchData () {
      const taxonomy = this.taxonomy

      fetchRunsByTaxonomy(taxonomy)
        .then(response => {
          this.search_result = response.data
        })
    },
    numericColumnTdAttrs (_row, _column) {
      return {
        style: 'text-align: center;'
      }
    },
    innerClick () {
      alert('Click!')
    }
  },
  watch: {
    // call again the method if the route changes
    $route: 'fetchData'
  }
}
</script>
