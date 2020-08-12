<template>
  <b-navbar>
    <template slot="brand">
      <b-navbar-item tag="router-link" :to="{path: '/'}">
        <img src="../assets/Logo_MCC.png" height="28" alt="Logo">
      </b-navbar-item>
    </template>
    <template slot="start">
      <router-link to="/" class="navbar-item" :class="{'is-active': this.$route.path.startsWith('/map')}">Map</router-link>
    </template>
    <template slot="end">
      <div class="navbar-item">
        <div class="buttons">
          <a class="button is-primary" href="https://www.mcc.tu-berlin.de/menue/forschung/projekte/simra/">
            <strong>Download App</strong>
          </a>
        </div>
      </div>
    </template>
  </b-navbar>
</template>

<script>
export default {
  name: "Navigation",
}
</script>

<style scoped lang="scss">
  nav.navbar {
    z-index: 500;
  }

</style>
