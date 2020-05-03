<template>
  <div style="height: 93%">
  <v-app-bar      
      dark
    >
      <v-app-bar-nav-icon></v-app-bar-nav-icon>

      <v-toolbar-title>Instance View</v-toolbar-title>

      <v-spacer></v-spacer>

      <v-menu
        left
        bottom
      >
        <template v-slot:activator="{ on }">
          <v-btn icon v-on="on">
            <v-icon>mdi-dots-vertical</v-icon>
          </v-btn>
        </template>

        <v-list>
          <v-list-item>
            <v-list-item-title v-on:click="()=>{showPolygon=!showPolygon; this.centerMap()}">{{showPolygon?'Ocultar':'Exibir'}} Polígono</v-list-item-title>
          </v-list-item>
          <v-list-item>
            <v-list-item-title v-on:click="()=>{showPanel=!showPanel}">Pontos Aleatórios</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </v-app-bar>
    <span v-if="showPanel">
      <v-row class="text-center">
        <v-col cols="10" offset="1">        
        <v-slider 
          v-model="numberOfCustomers_slider"
          class="align-center"
          max="100"
          min="5"
          hide-details
          :label="'Clientes: ' + numberOfCustomers_slider"
        >
      </v-slider>
        <v-slider 
          v-model="numberOfLockers_slider"
          class="align-center"
          max="20"
          min="2"
          hide-details
          :label="'Lockers: ' + numberOfLockers_slider"
        >
      </v-slider>
          <v-btn depressed small color="primary" v-on:click="drawRandomPoints">Gerar Pontos Aleatórios</v-btn>
        </v-col>
      </v-row>
    </span>
    <div style="height: 100%;">
      <v-card
        style="position:absolute; z-index: 1; margin-left: 10px; margin-top: 80px"
        height=90px
      >
        <v-card-text>
          <p>Customers: {{numberOfCustomers}}</p>
          <p>Lockers: {{numberOfLockers}}</p>
        </v-card-text>
      </v-card>
      <l-map
        style="height: 100%; width: 100%; z-index: 0"
        :zoom="zoom"
        :center="center"        
      >
        <l-tile-layer :url="url" :attribution=attribution></l-tile-layer>        
        <l-marker v-for="customer in customers" v-bind:key="customer.id" :lat-lng="customer.latlng" :icon=iconCustomer()></l-marker>
        <l-marker v-for="locker in lockers" v-bind:key="locker.id" :lat-lng="locker.latlng" :icon=iconLocker()></l-marker>
        <l-polygon :visible="showPolygon" :lat-lngs="pointsOfPolygon"></l-polygon>
      </l-map>      
    </div>    
  </div>
</template>

<script>

import L from "leaflet"
import { LMap, LTileLayer, LMarker, LPolygon } from 'vue2-leaflet';

export default {
  name: "Map",
  components:{
    LMap,
    LTileLayer,
    LMarker,
    LPolygon
  },
  data() {
    return {
      pointsOfPolygon: [],
      url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      zoom: 13,
      center: [-20.752327, -42.876433500000005],
      attribution: '&copy; <a href="https://openstreetmap.org/copyright">OpenStreetMap </a> | <a href="https://www.flaticon.com/free-icon/pin_2444532">Pixelmeetup</a> from <a href="https://www.flaticon.com/"> www.flaticon.com</a> contributors',
      numberOfCustomers: 25,
      numberOfLockers: 2,
      numberOfCustomers_slider: 25,
      numberOfLockers_slider: 2,
      customers: [],
      lockers: [],
      showPolygon: false,
      showPanel: false
    };
  },
  created(){
    this.setPolygon([
        [-20.706786, -42.82791],
        [-20.797868, -42.82791],
        [-20.797868, -42.924957],
        [-20.706786, -42.924957]
      ])
    this.drawRandomPoints()
  },
  methods: {
    setPolygon(points){
      this.pointsOfPolygon = points
      this.calcMinMax()
    },
    getRandomCustomers() {
      this.customers=[];
      for (let i = 0; i < this.numberOfCustomers; i++) {
          const long = Math.random() * (this.maxLong - this.minLong) + this.minLong;
          const lat = Math.random() * (this.maxLat - this.minLat) + this.minLat;
          this.customers.push({id:i, latlng:[long, lat]});
      }
    },
    getRandomLockers() {
      this.lockers=[];
      for (let i = 0; i < this.numberOfLockers; i++) {
          const long = Math.random() * (this.maxLong - this.minLong) + this.minLong;
          const lat = Math.random() * (this.maxLat - this.minLat) + this.minLat;
          this.lockers.push({id:i+this.numberOfCustomers, latlng:[long, lat]});
      }
    },
    calcMinMax(){ 
      this.minLong = this.pointsOfPolygon[0][0];
      this.maxLong = this.minLong;
      this.minLat = this.pointsOfPolygon[0][1];
      this.maxLat = this.minLat;
      for (let point of this.pointsOfPolygon) {
        if (point[0] < this.minLong)
          this.minLong = point[0]
        if (point[0] > this.maxLong)
          this.maxLong = point[0]
        if (point[1] < this.minLat)
          this.minLat = point[1]
        if (point[1] > this.maxLong)
          this.maxLat = point[1]
      }
    },
    centerMap(){
      this.center = [(this.maxLong - this.minLong) / 2 + this.minLong, (this.maxLat - this.minLat) / 2 + this.minLat];
    },
    drawRandomPoints(){
      this.numberOfCustomers = this.numberOfCustomers_slider
      this.numberOfLockers = this.numberOfLockers_slider
      this.centerMap()
      this.getRandomCustomers()
      this.getRandomLockers()
    },
    iconCustomer () {
      return L.icon({
        iconUrl: require('../assets/customer.png'),
        iconSize: [30, 30],
        iconAnchor: [20, 20]
      })    
    },
    iconLocker () {
      return L.icon({
        iconUrl: require('../assets/locker.png'),
        iconSize: [30, 30],
        iconAnchor: [20, 20]
      })    
    }
  }
};
</script>
