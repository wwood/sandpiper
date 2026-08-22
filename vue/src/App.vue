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
  .sunburst-block {
    width: 100%;
  }
  .sunburst-search {
    max-width: 30rem;
  }
  // Both SVGs have a square viewBox, so giving them a width and letting the
  // height follow keeps them inside their column instead of overflowing onto
  // the sections below, which is what a fixed pixel height did once the
  // columns stacked on narrow screens.
  .sunburst {
    display: block;
    width: 100%;
    height: auto;
    max-width: 900px;
    margin: 0 auto;
    font-size: 10px;
  }
  .sunburst-annotation {
    display: block;
    width: 100%;
    height: auto;
    max-width: 420px;
    margin: 0 auto;
    font-size: 30px;
  }
  .svg-link {
    fill: blue;
  }

  .sandpiperbackground {
    background-image: url("./assets/sandpiper.jpg");
    // `background-size: 100%` scales the image to the width of the element and
    // leaves its height to the aspect ratio, so the image was tiled a second
    // time down the page whenever the content was taller than that - which is
    // always the case on a narrow (mobile) viewport.
    background-size: cover;
    background-position: center center;
    background-repeat: no-repeat;
  }
  .footer-image {
    height: 50%;
  }

  // Long unbreakable strings - URLs shown as text, metapackage file names -
  // are wider than a phone screen and push the whole page sideways. Let them
  // wrap rather than overflow.
  p, li, td, th {
    overflow-wrap: break-word;
  }
}
</style>
