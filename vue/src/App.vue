<template>
  <div id="app">
    <b-navbar :centered="true" type="is-light">
        <template #start>
            <b-navbar-item tag="router-link" :to="{ path: '/' }">Home</b-navbar-item>
            <b-navbar-item tag="router-link" :to="{ path: '/Search' }">Search</b-navbar-item>

            <!-- <b-navbar-item>
            <b-navbar-dropdown label="Examples"> -->
              <b-navbar-item tag="router-link" :to="{ path: '/Run/ERR2000810' }">Neanderthal</b-navbar-item>
              <b-navbar-item tag="router-link" :to="{ path: '/Run/ERR1914274' }">Example 1</b-navbar-item>
            <!-- </b-navbar-dropdown>
            </b-navbar-item> -->

            <b-navbar-item tag="router-link" :to="{ path: '/About' }">About</b-navbar-item>
        </template>
    </b-navbar>
    <router-view />

    &nbsp;
    <footer class="footer">
      <div class="content">
        <div class="columns">

          <div class="column has-text-centered is-half is-offset-one-quarter">
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

          <div class="column is-one-eighth">
            <img src="./assets/cmr.png" width=200 />
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<style lang="scss">
#app {
//   font-family: Avenir, Helvetica, Arial, sans-serif;
//   -webkit-font-smoothing: antialiased;
//   -moz-osx-font-smoothing: grayscale;
//   text-align: center;
//   color: #2c3e50;

  // height: 800px;

  .pop-up {
    background-color: white;
    border: black;
    pointer-events: none;
    opacity: 0.92;
    font-size: 25px;
  }

//   .main-row {
//     height: 1800px;
//   }

//   .control-middle {
//     height: 600px;
//   }

//   .resizable {
//     margin-left: calc(50% - 50px);
//   }

//   .father {
//     position: relative;
//     width: 100%;
//     height: 100%;
//     display: flex;
//     justify-content: center;
//   }

  .sunburst {
    width: 100%;
    height: 700px;
    position: relative;
  }

//   .custo-checkbox {
//     display: flex;
//     justify-content: space-between;
//   }
// }

// #nav {
//   padding: 30px;

//   a {
//     font-weight: bold;
//     color: #2c3e50;

//     &.router-link-exact-active {
//       color: #42b983;
//     }
//   }
}
</style>
