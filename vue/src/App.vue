<template>
  <div id="app">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@mdi/font@5.8.55/css/materialdesignicons.min.css">
    <b-navbar :centered="true" type="is-light">
        <template #start>
            <b-navbar-item tag="router-link" :to="{ path: '/' }">Home</b-navbar-item>
            <b-navbar-item tag="router-link" :to="{ path: '/Search' }">Search</b-navbar-item>

            <b-navbar-item tag="router-link" :to="{ path: '/Run/SRR9841429' }">Example 1</b-navbar-item>
            <b-navbar-item tag="router-link" :to="{ path: '/Run/ERR1914274' }">Example 2</b-navbar-item>

            <b-navbar-item tag="router-link" :to="{ path: '/About' }">About</b-navbar-item>
        </template>
    </b-navbar>
    <router-view :key="$route.fullPath" />

    &nbsp;
    <footer class="footer">
      <div class="content">
        <div class="columns">

          <div class="column has-text-centered is-two-thirds is-offset-one-eigth">
            <p />
            <p />
          <p>
            Sandpiper was devised by the <a
            href="https://research.qut.edu.au/cmr/team/ben-woodcroft/">Woodcroft
            group</a> at the <a href="https://research.qut.edu.au/cmr">Centre
            for Microbiome Research</a>, <br /> School of Biomedical Sciences,
            Queensland University of Technology
          </p>
          </div>

          <div class="column is-one-eigth">
            <a href="https://research.qut.edu.au/cmr"><img src="./assets/cmr.png"  class="footer-image" /></a>
          </div>
          <div class="column is-one-eigth">
            <a href="https://qut.edu.au"><img src="./assets/QUT_SQUARE_RGB_SVG.svg" class="footer-image" /></a>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<style lang="scss">
#app {
  // sunburst-related styles
  .pop-up {
    background-color: white;
    border: black;
    pointer-events: none;
    opacity: 0.92;
    font-size: 25px;
  }
  .sunburst {
    width: 100%;
    height: 900px;
    position: relative;
    font-size: 10px;
  }
  .sunburst-annotation {
    width: 100%;
    position: relative;
    font-size: 30px;
  }
  .svg-link {
    fill: blue;
  }

  .sandpiperbackground {
    background-image: url("./assets/sandpiper.jpg");
    background-size: 100%;
    // height: 1000px
  }
  .footer-image {
    height: 50%;
  }
}
</style>
