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
          <v-slider
            v-model="numberOfDays_slider"
            class="align-center"
            max="10"
            min="2"
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
      <!--<v-btn depressed small color="primary" v-on:click="buildDistance"
        >Calcular Distâncias</v-btn
      >
      <p>{{ distance }}</p>
      <p>{{ customers }}</p>
      <p>{{ lockers }}</p>-->
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
                Customers:
                {{
                  customers.length === numberOfCustomers
                    ? numberOfCustomers
                    : `${customers.length}/${numberOfCustomers}`
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
                :lat-lng="[customer.latitude, customer.longitude]"
                :icon="iconCustomer()"
                v-on:click="customerClick(customer)"
              ></l-marker>
              <l-marker
                v-for="locker in lockers"
                v-bind:key="locker.id"
                :lat-lng="[locker.latitude, locker.longitude]"
                :icon="iconLocker()"
                v-on:click="lockerClick(locker)"
              ></l-marker>
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
      center: [-20.752327, -42.876433500000005],
      attribution:
        '&copy; <a href="https://openstreetmap.org/copyright">OpenStreetMap </a> | <a href="https://www.flaticon.com/free-icon/pin_2444532">Pixelmeetup</a> from <a href="https://www.flaticon.com/"> www.flaticon.com</a> contributors',
      numberOfCustomers: 5,
      numberOfLockers: 2,
      numberOfDays: 2,
      numberOfCustomers_slider: this.numberOfCustomers,
      numberOfLockers_slider: this.numberOfLockers,
      numberOfDays_slider: this.numberOfDays,
      // eslint-disable-next-line
      customers: [ { "id": 1, "latitude": -20.790452, "longitude": -42.856987, "day": 1}, { "id": 3, "latitude": -20.74617, "longitude": -42.84611, "day": 1}, { "id": 5, "latitude": -20.723942, "longitude": -42.896334, "day": 1 }, { "id": 6, "latitude": -20.736425, "longitude": -42.901754, "day": 1 }, { "id": 7, "latitude": -20.729555, "longitude": -42.853884, "day": 1 } ],
      // eslint-disable-next-line
      lockers: [ { "id": 2, "latitude": -20.745406, "longitude": -42.866753, "day": 1 }, { "id": 4, "latitude": -20.738825, "longitude": -42.856516, "day": 1 } ],
      genId: 1,
      showPolygon: false,
      showPanel: true,
      distance: [],
      log: "",
      currentCliente: 0,
      rateLimit: 1500,
      lastRequest: new Date(),
      processingClientes: false,
      processingLockers: false
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
            start: `${longitude.toFixed(6)},${latitude.toFixed(6)}`,
            end: `${longitude.toFixed(6)},${latitude.toFixed(6)}`
          }
        })
        .then(() => [latitude, longitude]);
    },
    createCoordenada() {
      const lng = this.randomLng();
      const lat = this.randomLat();
      return this.validatePoint(lat, lng);
    },
    createVertice(n, conjunto, type, _day) {
      if (type === 1) this.processingClientes = true;
      else this.processingLockers = true;
      this.createCoordenada()
        .then(latlng => {
          conjunto.push({
            id: this.genId++,
            latitude: latlng[0],
            longitude: latlng[1],
            day: _day
          });
          if (conjunto.length < n) {
            this.createVertice(n, conjunto, type, _day);
          } else {
            if (type === 1) this.processingClientes = false;
            else this.processingLockers = false;
          }
        })
        .catch(err => {
          this.createVertice(n, conjunto, type, _day);
          console.log(err);
        });
    },
    createInstance() {
      this.genId = 1;
      this.customers = [];
      this.createVertice(this.numberOfCustomers, this.customers, 1, 1);
      this.lockers = [];
      this.createVertice(this.numberOfLockers, this.lockers, 2, 1);
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
            start: `${points[i].longitude.toFixed(6)},${points[
              i
            ].latitude.toFixed(6)}`,
            end: `${points[j].longitude.toFixed(6)},${points[
              j
            ].latitude.toFixed(6)}`
          }
        })
        .then(val => [
          val.data.features[0].properties.segments[0].distance,
          points,
          i,
          j
        ])
        .catch(err => console.log(err));
    },
    getDistance(points, distance, i, j) {
      this.getDistanceAtoB(points, i, j, points.length)
        .then(([distanceAtoB, points, i, j]) => {
          distance[i][j] = distanceAtoB;
          j++;
          if (j === i) j++;
          if (j >= points.length) {
            j = 0;
            i++;
          }
          if (j < points.length) {
            this.getDistance(points, distance, i, j);
          }
        })
        .catch(err => console.log(err));
    },
    buildDistance() {
      let points = this.customers;
      points.concat(this.lockers);
      this.distance = Array(points.length)
        .fill()
        .map(() => Array(points.length).fill(0));
      this.getDistance(points, this.distance, 0, 1);
    },
    customerClick(customer) {
      alert(
        `Cliente\nID: ${customer.id}\nLatitude: ${customer.latitude} \nLongitude: ${customer.longitude} \nDia: ${customer.day}`
      );
    },
    lockerClick(locker) {
      alert(
        `Locker\nID: ${locker.id}\nLatitude: ${locker.latitude} \nLongitude: ${locker.longitude} \nDia: ${locker.day}`
      );
    }
  }
};
</script>
