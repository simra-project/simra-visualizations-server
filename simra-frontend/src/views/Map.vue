<template>
  <l-map :center="center" :zoom="zoom" id="main-map" ref="map">
    <l-tile-layer url="http://{s}.tile.osm.org/{z}/{x}/{y}.png" />
    <l-tile-layer url="http://79.224.175.84//tiles/simra_rides/{z}/{x}/{y}.png" />
    <l-geo-json :geojson="incidents"/>
  </l-map>
</template>

<script>
import { LMap, LTileLayer, LGeoJson, LMarker } from "vue2-leaflet";
import L from 'leaflet';

// eslint-disable-next-line
delete L.Icon.Default.prototype._getIconUrl
// eslint-disable-next-line
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png')
})

export default {
  name: "Map",
  components: {
    LMap,
    LTileLayer,
    LGeoJson
  },
  data() {
    return {
      center: [52.5125322, 13.3269446],
      zoom: 15,
      incidents: []
    }
  },
  methods: {
    updateIncidents() {
      const bboxFilter = "&in_bbox=" + this.$refs.map.mapObject.getBounds().toBBoxString()
      fetch("http://localhost:8000/api/incidents?" + bboxFilter).then(raw => raw.json()).then(data => {
        console.log(data)
        this.incidents = data
      })
    }
  },
  async mounted() {
    this.updateIncidents()
  }
}
</script>

<style scoped lang="scss">

  #main-map {
    height: 100%;
    width: 100%;
    flex: 1 0;
  }

</style>
