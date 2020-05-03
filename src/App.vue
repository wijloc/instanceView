<template>
  <v-app>    
    <v-content>
      <Map />
    </v-content>
  </v-app>
</template>
<script>
import Map from "./components/Map";

export default {
  name: "App",

  components: {
    Map
  },

  data: () => ({
    //
  })
};
</script>
