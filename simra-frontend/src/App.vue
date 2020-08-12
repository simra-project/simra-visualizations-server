<template>
  <div id="app">
    <Navigation/>
    <section class="hero is-fullheight-with-navbar">
      <router-view></router-view>
    </section>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator';
import Navigation from './components/Navigation.vue';

@Component({
  components: {
    Navigation,
  },
})
export default class App extends Vue {}
</script>

<style lang="scss">
  .hero {
    background-color: #f3f3f3;
    border-top: 1px solid #ddd;
  }

  // Import Bulma's core
  @import "~bulma/sass/utilities/_all";

  // Set your colors
  $primary: hsl(217, 71%, 53%);
  $primary-invert: hsl(0, 0%, 100%);

  // Setup $colors to use as bulma classes (e.g. 'is-twitter')
  $colors: (
    "white": ($white, $black),
    "black": ($black, $white),
    "light": ($light, $light-invert),
    "dark": ($dark, $dark-invert),
    "primary": ($primary, $primary-invert),
    "info": ($info, $info-invert),
    "success": ($success, $success-invert),
    "warning": ($warning, $warning-invert),
    "danger": ($danger, $danger-invert)
  );

  // Links
  $link: $primary;
  $link-invert: $primary-invert;
  $link-focus-border: $primary;

  // Import Bulma and Buefy styles
  @import "~bulma";
  @import "~buefy/src/scss/buefy";
</style>
