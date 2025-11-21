<template>
  <div>
    &nbsp;
    <div class="container">
      <section>
        <h3 class="title">Submitter information</h3>
        <RunMetadataTable :table_data="this.mdata.contact_metadata"  />
      </section>
    </div>

    &nbsp;
    <div class="container">
      <section>
        <h3 class="title">Sample information</h3>
        <div v-if="lat_lon() !== null">
          <!-- I cannot get center.sync to reset when reset_map() is clicked, oh well -->
          <l-map :style="map_style" :zoom.sync="zoom" :center.sync="center">
            <l-tile-layer :url="url" :attribution="attribution" />
            <l-marker :lat-lng="lat_lon()" />
          </l-map>
          <div @click="reset_map()"><b-icon icon="refresh" size="is-small" /> reset zoom</div>
          <br />
        </div>
        <RunMetadataTable :table_data="this.mdata.sample_info_metadata"  />
      </section>
    </div>

    &nbsp;
    <div class="container">
      <section>
        <h3 class="title">Sequencing information</h3>
        <RunMetadataTable :table_data="this.mdata.sequencing_metadata"  />
      </section>
    </div>

    &nbsp;
    <div class="container">
      <section>
        <h3 class="title">Other identifiers</h3>
        <RunMetadataTable :table_data="this.mdata.identity_metadata"  />
      </section>
    </div>

    &nbsp;
    <div class="container">
      <section>
        <h3 class="title">Study links</h3>
        <div v-if="Object.keys(gatherMetadata ('study_links')).length===0">
          <p>No linked studies recorded</p>
        </div>
        <div v-else>
          <b-table :data="gatherMetadata ('study_links')" :columns="studyLinksColumns()" :striped="true" />
        </div>
      </section>
    </div>

  </div>
</template>

<script>

// If you need to reference 'L', such as in 'L.icon', then be sure to
// explicitly import 'leaflet' into your component
// import L from 'leaflet'
import { LMap, LTileLayer, LMarker } from 'vue2-leaflet'

// Make the marker appear https://vue2-leaflet.netlify.app/quickstart/#marker-icons-are-missing
import { Icon, latLng } from 'leaflet'

import RunMetadataTable from '@/components/RunMetadataTable.vue'

delete Icon.Default.prototype._getIconUrl
Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png')
})

const default_zoom = 0.5

export default {
  name: 'RunMetadata',
  props: ['mdata','mdata_parsed'],
  components: {
    LMap,
    LTileLayer,
    LMarker,
    RunMetadataTable
  },
  data () {
    return {
      medata: this.mdata,
      url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      attribution:
        '&copy; <a target="_blank" href="http://osm.org/copyright">OpenStreetMap</a> contributors',
      zoom: default_zoom,
      center: latLng(0, 0),
      bounds: null
    }
  },
  mounted () {
    this.center = this.get_default_map_center()
  },
  computed: {
    map_style: function () {
      const style = 'height: 300px; width: '
      // Make the width fit for smaller screens, but max out the width.
      if (window.innerWidth < 600) {
        return style+'100%'
      } else {
        return style+'550px'
      }
    },
  },
  methods: {
    get_default_map_center: function () {
      const lat_lon = this.lat_lon()
      if (lat_lon !== null) {
        // Near the poles, the map is too small and so the marker can be hidden
        if (lat_lon[0] > 45) {
          return latLng(45.0, lat_lon[1])
        } else if (lat_lon[0] < -45) {
          return latLng(-45.0, lat_lon[1])
        } else {
          return latLng(0, lat_lon[1])
        }
      } else {
        return latLng(0, 0)
      }
    },
    reset_map: function () {
      // Setting the center here doesn't appear to have any effect
      this.center = this.get_default_map_center()
      // Zoom works though
      this.zoom = default_zoom
    },
    // Data to be put in the general metadata. This method is actually mostly
    // dead code now, but kept as it is used in one place
    gatherMetadata (section) {
      const toReturn = []
      Object.keys(this.mdata).forEach(key => {
        const v = this.mdata[key]
        if (section==='general') {
          if (!['biosample_attributes','study_links','parsed_sample_attributes','study_abstract','study_title'].includes(key) && v !== null) {
            toReturn.push({
              k: key,
              value: v
            })
          }
        } else if (section==='study_links' && key === 'study_links') {
          v.forEach(link => {
            if (typeof link['database'] !== 'undefined') {
              if (link['database'].toLowerCase() === 'pubmed'){
                toReturn.push({
                  k: link['database'],
                  value: '<a href="https://www.ncbi.nlm.nih.gov/pubmed?term='+link['study_id']+'">'+link['study_id']+'</a>'
                })
              } else {
                toReturn.push({
                  k: link['database'],
                  value: link['study_id']
                })
              }
            } else {
              toReturn.push({
                k: link.label,
                value: '<a href="'+link.url+'">'+link.url+'</a>'
              })
            }
          })
        } else {
          if (key === section) {
            Object.keys(v).forEach(k => {
              if (v[k] !== null) {
                toReturn.push({
                  k: k,
                  value: v[k]
                })
              }
            })
          }
        }
      })
      return toReturn
    },
    studyLinksColumns () {
      return [{ label: 'database', field: 'k' }, { label: 'id', field: 'value' }]
    },
    lat_lon () {
      const parsed_data = this.mdata_parsed
      const lat = parsed_data.latitude
      const lon = parsed_data.longitude
      if (lat !== null && lon !== null) {
        return [lat, lon]
      } else {
        return null
      }
    }
  }
}
</script>
