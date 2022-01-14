<template>
  <div id="app">
    <div id="nav">
      <router-link to="/">Home</router-link> |
      <router-link to="/Search">Search</router-link> |
      <router-link to="/Run/1234">Run</router-link>
    </div>
    <router-view/>
  </div>
</template>

<style lang="scss">
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;

  height: 800px;

  .pop-up {
    background-color: white;
    border: black;
    pointer-events: none;
    opacity: 0.92;
  }

  .main-row {
    height: 1800px;
  }

  .control-middle {
    height: 600px;
  }

  .resizable {
    margin-left: calc(50% - 50px);
  }

  .father {
    position: relative;
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
  }

  .sunburst {
    width: 100%;
    height: 700px;
    position: relative;
  }

  .custo-checkbox {
    display: flex;
    justify-content: space-between;
  }
}

#nav {
  padding: 30px;

  a {
    font-weight: bold;
    color: #2c3e50;

    &.router-link-exact-active {
      color: #42b983;
    }
  }
}
</style>
