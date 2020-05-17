<template>
  <div style="height: 93%">
    <v-app-bar dark>
      <v-app-bar-nav-icon></v-app-bar-nav-icon>

      <v-toolbar-title>Instance View</v-toolbar-title>

      <v-spacer></v-spacer>

      <v-menu left bottom>
        <template v-slot:activator="{ on }">
          <v-btn icon v-on="on">
            <v-icon>mdi-dots-vertical</v-icon>
          </v-btn>
        </template>

        <v-list>
          <v-list-item>
            <v-list-item-title
              v-on:click="
                () => {
                  showPolygon = !showPolygon;
                  this.centerMap();
                }
              "
              >{{ showPolygon ? "Ocultar" : "Exibir" }}
              Polígono
            </v-list-item-title>
          </v-list-item>
          <v-list-item>
            <v-list-item-title v-on:click="buildDistance">
              Calcular Distâncias
            </v-list-item-title>
          </v-list-item>
          <v-list-item>
            <v-list-item-title
              v-on:click="
                () => {
                  showPanel = !showPanel;
                }
              "
              >Pontos Aleatórios
            </v-list-item-title>
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
            min="1"
            hide-details
            :label="'Clientes: ' + numberOfCustomers_slider"
          >
          </v-slider>
          <v-slider
            v-model="numberOfLockers_slider"
            class="align-center"
            max="20"
            min="1"
            hide-details
            :label="'Lockers: ' + numberOfLockers_slider"
          >
          </v-slider>
          <v-slider
            v-model="numberOfDays_slider"
            class="align-center"
            max="10"
            min="1"
            hide-details
            :label="'Dias: ' + numberOfDays_slider"
          >
          </v-slider>
          <v-btn depressed small color="primary" v-on:click="drawRandomPoints"
            >Gerar Pontos Aleatórios</v-btn
          >
        </v-col>
      </v-row>
    </span>
    <div style="height: 100%;">
      <v-row class="text-center">
        <v-col cols="10" offset="1">
          <v-card
            style="position:absolute; z-index: 1; margin-left: 10px; margin-top: 80px"
            height="90px"
          >
            <v-card-text>
              <p>
                <span v-if="processingClientes">
                  <v-progress-circular
                    indeterminate
                    color="red"
                    size="12"
                    width="2"
                  ></v-progress-circular>
                </span>
                Clientes:
                {{
                  customers.length === numberOfCustomers * numberOfDays
                    ? customers.length
                    : `${customers.length}/${numberOfCustomers * numberOfDays}`
                }}
              </p>
              <p>
                <span v-if="processingLockers">
                  <v-progress-circular
                    indeterminate
                    color="blue"
                    size="12"
                    width="2"
                  ></v-progress-circular>
                </span>
                Lockers:
                {{
                  lockers.length === numberOfLockers
                    ? numberOfLockers
                    : `${lockers.length}/${numberOfLockers}`
                }}
              </p>
            </v-card-text>
          </v-card>
          <div style="height: 600px">
            <l-map
              style="height: 100%; width: 100%; z-index: 0"
              :zoom="zoom"
              :center="center"
            >
              <l-tile-layer
                :url="url"
                :attribution="attribution"
              ></l-tile-layer>
              <l-marker
                v-for="customer in customers"
                v-bind:key="customer.id"
                :lat-lng.sync="customer.position"
                :icon="iconCustomer()"
                v-on:click="customerClick(customer)"
                :draggable="true"
              ></l-marker>
              <l-marker
                v-for="locker in lockers"
                v-bind:key="locker.id"
                :lat-lng.sync="locker.position"
                :icon="iconLocker()"
                v-on:click="lockerClick(locker)"
                :draggable="true"
              ></l-marker>
              <l-marker :lat-lng.sync="deposito.position" :draggable="true">
              </l-marker>
              <l-polygon
                :visible="showPolygon"
                :lat-lngs="pointsOfPolygon"
              ></l-polygon>
            </l-map>
          </div>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="10" offset="1">
          <p>{{ deposito }}</p>
          <p>{{ customers }}</p>
          <p>{{ lockers }}</p>
          <p>{{ distance }}</p>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="10" offset="1">
          <textarea v-model="log" style="width: 100%"></textarea>
        </v-col>
      </v-row>
    </div>
  </div>
</template>
<script>
import L from "leaflet";
import { LMap, LTileLayer, LMarker, LPolygon } from "vue2-leaflet";
import axios from "axios";

export default {
  name: "Map",
  components: {
    LMap,
    LTileLayer,
    LMarker,
    LPolygon
  },
  data() {
    return {
      pointsOfPolygon: [],
      url: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
      zoom: 13,
      center: [-20.752327, -42.876433],
      attribution:
        '&copy; <a href="https://openstreetmap.org/copyright">OpenStreetMap </a> | <a href="https://www.flaticon.com/free-icon/pin_2444532">Pixelmeetup</a> from <a href="https://www.flaticon.com/"> www.flaticon.com</a> contributors',
      numberOfCustomers: 0,
      numberOfLockers: 0,
      numberOfDays: 0,
      numberOfCustomers_slider: 1,
      numberOfLockers_slider: 1,
      numberOfDays_slider: 1,
      // eslint-disable-next-line
      customers: [],
      // eslint-disable-next-line
      lockers: [],
      genId: 1,
      showPolygon: false,
      showPanel: true,
      // eslint-disable-next-line
      distance: [],
      log: "",
      currentCliente: 0,
      rateLimit: 1500,
      lastRequest: new Date(),
      processingClientes: false,
      processingLockers: false,
      // eslint-disable-next-line
      deposito: { "position": { "lat": -20.752327, "lng": -42.876433 } }//{ position: { lat: -20.752327, lng: -42.876433 }      
    };
  },
  created() {
    this.setPolygon([
      [-42.82791, -20.706786],
      [-42.82791, -20.797868],
      [-42.924957, -20.797868],
      [-42.924957, -20.706786]
    ]);
  },
  methods: {
    setPolygon(points) {
      this.pointsOfPolygon = points;
      this.calcMinMax();
    },
    formatLatLng(val) {
      return parseInt(val * 1000000) / 1000000;
    },
    randomLat() {
      return this.formatLatLng(
        Math.random() * (this.maxLat - this.minLat) + this.minLat
      );
    },
    randomLng() {
      return this.formatLatLng(
        Math.random() * (this.maxLong - this.minLong) + this.minLong
      );
    },
    waitRateLimit() {
      while (
        new Date().getTime() - this.lastRequest.getTime() <
        this.rateLimit
      ) {
        //
      }
      this.lastRequest = new Date();
      this.log += `Solicitação em: ${this.lastRequest}\n`;
    },
    validatePoint(latitude, longitude) {
      this.waitRateLimit();
      return axios
        .create({
          baseURL: "https://api.openrouteservice.org/v2/directions/driving-car"
        })
        .get("", {
          method: "GET",
          headers: {
            Authorization:
              "5b3ce3597851110001cf624858ffbe94f1f945c792d6183667844b71",
            "Content-Type": "application/json"
          },
          params: {
            start: `${longitude},${latitude}`,
            end: `${longitude},${latitude}`
          }
        })
        .then(() => [latitude, longitude]);
    },
    createCoordenada() {
      const lng = this.randomLng();
      const lat = this.randomLat();
      return this.validatePoint(lat, lng)
        .then(latlng => latlng)
        .catch(() => {
          return this.createCoordenada();
        });
    },
    createCustomer(conjunto, _day) {
      return this.createCoordenada()
        .then(latlng => {
          return (
            conjunto.push({
              id: this.genId++,
              position: {
                lat: latlng[0],
                lng: latlng[1]
              },
              day: _day
            }) - 1
          );
        })
        .catch(err => {
          console.log(err);
        });
    },
    createLocker(conjunto) {
      return this.createCoordenada()
        .then(latlng => {
          return (
            conjunto.push({
              id: this.genId++,
              position: {
                lat: latlng[0],
                lng: latlng[1]
              }
            }) - 1
          );
        })
        .catch(err => {
          console.log(err);
        });
    },
    async createInstance() {
      this.genId = 1;
      this.customers = [];

      this.processingClientes = true;
      for (let j = 1; j <= this.numberOfDays; j++)
        for (let i = 0; i < this.numberOfCustomers; i++)
          await this.createCustomer(this.customers, j);

      this.processingClientes = false;

      this.processingLockers = true;
      this.lockers = [];
      for (let i = 0; i < this.numberOfLockers; i++)
        await this.createLocker(this.lockers);
      this.processingLockers = false;
    },
    calcMinMax() {
      this.minLong = this.pointsOfPolygon[0][0];
      this.maxLong = this.minLong;
      this.minLat = this.pointsOfPolygon[0][1];
      this.maxLat = this.minLat;
      for (let point of this.pointsOfPolygon) {
        if (point[0] < this.minLong) this.minLong = point[0];
        if (point[0] > this.maxLong) this.maxLong = point[0];
        if (point[1] < this.minLat) this.minLat = point[1];
        if (point[1] > this.maxLong) this.maxLat = point[1];
      }
    },
    centerMap() {
      this.center = [
        (this.maxLat - this.minLat) / 2 + this.minLat,
        (this.maxLong - this.minLong) / 2 + this.minLong
      ];
    },
    drawRandomPoints() {
      this.numberOfCustomers = this.numberOfCustomers_slider;
      this.numberOfLockers = this.numberOfLockers_slider;
      this.numberOfDays = this.numberOfDays_slider;
      this.centerMap();
      this.createInstance();
    },
    iconCustomer() {
      return L.icon({
        iconUrl: require("../assets/customer.png"),
        iconSize: [30, 30],
        iconAnchor: [20, 20]
      });
    },
    iconLocker() {
      return L.icon({
        iconUrl: require("../assets/locker.png"),
        iconSize: [30, 30],
        iconAnchor: [20, 20]
      });
    },
    getDistanceAtoB(points, i, j) {
      this.waitRateLimit();
      return axios
        .create({
          baseURL: "https://api.openrouteservice.org/v2/directions/driving-car"
        })
        .get("", {
          method: "GET",
          headers: {
            Authorization:
              "5b3ce3597851110001cf624858ffbe94f1f945c792d6183667844b71",
            "Content-Type": "application/json"
          },
          params: {
            start: `${points[i].position.lng},${points[i].position.lat}`,
            end: `${points[j].position.lng},${points[j].position.lat}`
          }
        })
        .then(val => val.data.features[0].properties.segments[0].distance)
        .catch(err => {
          console.log(err);
          return this.getDistanceAtoB(points, i, j);
        });
    },
    async buildDistance() {
      let points = [
        {
          id: 0,
          position: {
            latitude: this.deposito.position.lat,
            longitude: this.deposito.position.lng
          }
        }
      ];
      points = points.concat(this.customers);
      points = points.concat(this.lockers);
      this.distance = Array(points.length)
        .fill()
        .map(() => Array(points.length).fill(0));
      for (let i = 0; i < points.length; i++)
        for (let j = 0; j < points.length; j++)
          await this.getDistanceAtoB(points, i, j).then(
            distance => (this.distance[i][j] = distance || 0)
          );
    },
    customerClick(customer) {
      alert(
        `Cliente\nID: ${customer.id}\nLatitude: ${customer.latitude} \nLongitude: ${customer.longitude} \nDia: ${customer.day}`
      );
    },
    lockerClick(locker) {
      alert(
        `Locker\nID: ${locker.id}\nLatitude: ${locker.latitude} \nLongitude: ${locker.longitude}`
      );
    }
  }
};
</script>
