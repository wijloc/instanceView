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
            <v-list-item-title
              v-on:click="
                () => {
                  showPanel = !showPanel;
                }
              "
              >Pontos Aleatórios
            </v-list-item-title>
          </v-list-item>
          <v-list-item>
            <v-list-item-title v-on:click="getInstanceText">
              Gerar Instância
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
            max="500"
            min="1"
            hide-details
            :label="'Clientes: ' + numberOfCustomers_slider"
          >
          </v-slider>
          <v-slider
            v-model="numberOfLockers_slider"
            class="align-center"
            max="50"
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
          <v-range-slider
            v-model="demandRange"
            min="1"
            max="1000"
            :label="
              'Random Demand Limits: ' +
                this.demandRange[0] +
                ' ' +
                this.demandRange[1]
            "
          ></v-range-slider>
          <v-checkbox v-model="withDayProperty" label="With Day Property" />
          <v-checkbox v-model="withDemand" label="With Random Demand" />
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
                :icon="iconCustomer(customer.id)"
                v-on:click="customerClick(customer)"
                :draggable="true"
              >
                <l-tooltip :content="customer.id.toString()"></l-tooltip>
              </l-marker>
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
      <v-row class="text-center">
        <v-col cols="10" offset="1">
          <v-btn depressed small color="primary" v-on:click="getInstanceText"
            >Imprimir Instância</v-btn
          >
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="10" offset="1">
          <v-textarea
            label="Instance:"
            v-model="instance"
            style="font-family: 'monospace'"
            :auto-grow="true"
          ></v-textarea>
        </v-col>
      </v-row>
    </div>
  </div>
</template>
<script>
import L from "leaflet";
import { LMap, LTileLayer, LMarker, LPolygon, LTooltip } from "vue2-leaflet";
import axios from "axios";

export default {
  name: "Map",
  components: {
    LMap,
    LTileLayer,
    LMarker,
    LPolygon,
    LTooltip
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
      currentCliente: 0,
      rateLimit: 1500,
      lastRequest: new Date(),
      processingClientes: false,
      processingLockers: false,
      // eslint-disable-next-line
      
      //milan deposit
      //deposito: { position: { lat: 45.455796, lng: 9.173155 } },

      //vicosa deposit
      deposito: { position: { lat: -20.752327, lng: -42.876433 } },
      instance: "",
      withDayProperty: false,
      withDemand: true,
      demandRange: [10, 50]
    };
  },
  created() {
    //Viçosa Polygon:
    this.setPolygon([
      [-20.706786, -42.82791],
      [-20.706786, -42.924957],
      [-20.797868, -42.924957],
      [-20.797868, -42.82791]
    ]);
    //this.loadInstance();
    //Milan Polygon:
    /*this.setPolygon([
      [45.498647, 9.147663],
      [45.498647, 9.228516],
      [45.438815, 9.228516],
      [45.438815, 9.147663]
    ]);*/
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
          let customer = {
            id: this.genId++,
            position: {
              lat: latlng[0],
              lng: latlng[1]
            }
          };

          if (this.withDayProperty) {
            customer = { ...customer, day: _day };
          }

          if (this.withDemand) {
            const demand = Math.floor(
              Math.floor(
                Math.random() * (this.demandRange[1] - this.demandRange[0])
              ) + this.demandRange[0]
            );
            customer = { ...customer, demand };
          }

          return conjunto.push(customer) - 1;
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
      this.minLong = this.pointsOfPolygon[0][1];
      this.maxLong = this.minLong;
      this.minLat = this.pointsOfPolygon[0][0];
      this.maxLat = this.minLat;
      for (let point of this.pointsOfPolygon) {
        if (point[1] < this.minLong) this.minLong = point[1];
        if (point[1] > this.maxLong) this.maxLong = point[1];
        if (point[0] < this.minLat) this.minLat = point[0];
        if (point[0] > this.maxLat) this.maxLat = point[0];
      }
    },
    centerMap() {
      this.center = [
        (this.maxLat - this.minLat) / 2 + this.minLat,
        (this.maxLong - this.minLong) / 2 + this.minLong
      ];
    },
    async drawRandomPoints() {
      this.numberOfCustomers = this.numberOfCustomers_slider;
      this.numberOfLockers = this.numberOfLockers_slider;
      this.numberOfDays = this.numberOfDays_slider;
      this.centerMap();
      await this.createInstance();
      this.getInstanceText();
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
    customerClick(customer) {
      /*alert(
        `Cliente\nID: ${customer.id}\nLatitude: ${customer.position.lat} \nLongitude: ${customer.position.lng} \nDia: ${customer.day}`
      );*/
      console.log(customer);
    },
    lockerClick(locker) {
      /*alert(
        `Locker\nID: ${locker.id}\nLatitude: ${locker.position.lat} \nLongitude: ${locker.position.lng}`
      );*/
      console.log(locker);
    },
    getInstanceText() {
      var output = "";
      output = `#name\n`;
      output += `instance\n`;
      output += `\n`;
      output += `#numDepots\n`;
      output += `1\n`;
      output += `\n`;
      if (this.withDayProperty) {
        output += `#numDays\n`;
        output += `${this.numberOfDays}\n`;
        output += `\n`;
      }
      output += `#numLockers\n`;
      output += `${this.numberOfLockers}\n`;
      output += `\n`;
      output += `#numMunicipalities\n`;
      output += `${this.customers.length}\n`;
      output += `\n`;
      output += `#depots\n`;
      output += `+----+------------------+--------+--------------+---------------+---------------+\n`;
      output += `| id |       name       | region |   latitude   |   longitude   | # technicians |\n`;
      output += `+----+------------------+--------+--------------+---------------+---------------+\n`;
      output += `    0  DEPOT                   DM    ${this.deposito.position.lat}     ${this.deposito.position.lng}               1 \n`;
      output += `\n#municipalities\n`;
      output += `+----+---------------------------+--------------+---------------+\n`;
      output += `| id |        city_name          |   latitude   |   longitude   |\n`;
      output += `+----+---------------------------+--------------+---------------+\n`;
      for (let i = 0; i < this.customers.length; i++) {
        output += `${this.customers[i].id} CUSTOMER ${this.customers[i].position.lat} ${this.customers[i].position.lng}`;
        if (this.customers[i].demand) {
          output += ` ${this.customers[i].demand}`;
        }
        output += `\n`;
      }
      for (let i = 0; i < this.lockers.length; i++) {
        output += `${this.lockers[i].id} LOCKER ${this.lockers[i].position.lat} ${this.lockers[i].position.lng}\n`;
      }
      this.instance = output;
    },
    loadInstance() {
      this.customers = [
        { id: 1, position: { lat: -20.762852, lng: -42.900547 }, day: 1 },
        { id: 2, position: { lat: -20.744063, lng: -42.852214 }, day: 1 },
        { id: 3, position: { lat: -20.759264, lng: -42.904449 }, day: 1 },
        { id: 4, position: { lat: -20.734146, lng: -42.891618 }, day: 1 },
        { id: 5, position: { lat: -20.753156, lng: -42.842658 }, day: 1 },
        { id: 6, position: { lat: -20.762388, lng: -42.908312 }, day: 1 },
        {
          id: 7,
          position: { lat: -20.7708810031881, lng: -42.8968048095703 },
          day: 1
        },
        { id: 8, position: { lat: -20.753822, lng: -42.861433 }, day: 1 },
        { id: 9, position: { lat: -20.715244, lng: -42.869973 }, day: 1 },
        { id: 10, position: { lat: -20.742468, lng: -42.845646 }, day: 1 },
        { id: 11, position: { lat: -20.762222, lng: -42.903698 }, day: 1 },
        { id: 12, position: { lat: -20.734997, lng: -42.892437 }, day: 1 },
        { id: 13, position: { lat: -20.771844, lng: -42.906055 }, day: 1 },
        { id: 14, position: { lat: -20.731836, lng: -42.909953 }, day: 1 },
        { id: 15, position: { lat: -20.775965, lng: -42.86444 }, day: 1 },
        { id: 16, position: { lat: -20.716122, lng: -42.871662 }, day: 1 },
        { id: 17, position: { lat: -20.777455, lng: -42.833024 }, day: 1 },
        { id: 18, position: { lat: -20.747153, lng: -42.86362 }, day: 1 },
        { id: 19, position: { lat: -20.757167, lng: -42.887067 }, day: 1 },
        { id: 20, position: { lat: -20.790603, lng: -42.870907 }, day: 1 },
        { id: 21, position: { lat: -20.791572, lng: -42.90793 }, day: 1 },
        { id: 22, position: { lat: -20.732011, lng: -42.831552 }, day: 1 },
        { id: 23, position: { lat: -20.754001, lng: -42.83125 }, day: 1 },
        { id: 24, position: { lat: -20.762831, lng: -42.92287 }, day: 1 },
        { id: 25, position: { lat: -20.745941, lng: -42.881009 }, day: 1 },
        { id: 26, position: { lat: -20.762127, lng: -42.868338 }, day: 1 },
        { id: 27, position: { lat: -20.733917, lng: -42.918125 }, day: 1 },
        { id: 28, position: { lat: -20.786103, lng: -42.869363 }, day: 1 },
        { id: 29, position: { lat: -20.755241, lng: -42.908278 }, day: 1 },
        { id: 30, position: { lat: -20.764688, lng: -42.843856 }, day: 1 },
        { id: 31, position: { lat: -20.767685, lng: -42.854303 }, day: 1 },
        { id: 32, position: { lat: -20.764799, lng: -42.851068 }, day: 1 },
        { id: 33, position: { lat: -20.791047, lng: -42.899753 }, day: 1 },
        { id: 34, position: { lat: -20.720199, lng: -42.863587 }, day: 1 },
        { id: 35, position: { lat: -20.770436, lng: -42.887853 }, day: 1 },
        { id: 36, position: { lat: -20.766384, lng: -42.848325 }, day: 1 },
        { id: 37, position: { lat: -20.797222, lng: -42.897611 }, day: 1 },
        { id: 38, position: { lat: -20.764459, lng: -42.849685 }, day: 1 },
        { id: 39, position: { lat: -20.770394, lng: -42.879163 }, day: 1 },
        { id: 40, position: { lat: -20.748909, lng: -42.883271 }, day: 1 },
        { id: 41, position: { lat: -20.732516, lng: -42.893075 }, day: 1 },
        { id: 42, position: { lat: -20.709688, lng: -42.864453 }, day: 1 },
        { id: 43, position: { lat: -20.794318, lng: -42.85068 }, day: 1 },
        { id: 44, position: { lat: -20.740765, lng: -42.841317 }, day: 1 },
        { id: 45, position: { lat: -20.734285, lng: -42.901262 }, day: 1 },
        { id: 46, position: { lat: -20.783761, lng: -42.878386 }, day: 1 },
        { id: 47, position: { lat: -20.76937, lng: -42.842306 }, day: 1 },
        { id: 48, position: { lat: -20.738635, lng: -42.845423 }, day: 1 },
        { id: 49, position: { lat: -20.74554, lng: -42.870786 }, day: 1 },
        { id: 50, position: { lat: -20.707989, lng: -42.906675 }, day: 1 },
        { id: 51, position: { lat: -20.744827, lng: -42.924312 }, day: 1 },
        { id: 52, position: { lat: -20.788826, lng: -42.879109 }, day: 1 },
        { id: 53, position: { lat: -20.793696, lng: -42.853454 }, day: 1 },
        { id: 54, position: { lat: -20.759505, lng: -42.891687 }, day: 1 },
        { id: 55, position: { lat: -20.719754, lng: -42.840425 }, day: 1 },
        { id: 56, position: { lat: -20.725735, lng: -42.880585 }, day: 1 },
        { id: 57, position: { lat: -20.777647, lng: -42.899811 }, day: 1 },
        { id: 58, position: { lat: -20.7593, lng: -42.837838 }, day: 1 },
        { id: 59, position: { lat: -20.741087, lng: -42.906947 }, day: 1 },
        { id: 60, position: { lat: -20.779731, lng: -42.863335 }, day: 1 },
        { id: 61, position: { lat: -20.707248, lng: -42.886961 }, day: 1 },
        { id: 62, position: { lat: -20.747851, lng: -42.922423 }, day: 1 },
        { id: 63, position: { lat: -20.717533, lng: -42.890579 }, day: 1 },
        { id: 64, position: { lat: -20.777619, lng: -42.904008 }, day: 1 },
        { id: 65, position: { lat: -20.772647, lng: -42.882844 }, day: 1 },
        { id: 66, position: { lat: -20.711953, lng: -42.90463 }, day: 1 },
        { id: 67, position: { lat: -20.715389, lng: -42.865307 }, day: 1 },
        { id: 68, position: { lat: -20.737101, lng: -42.893272 }, day: 1 },
        { id: 69, position: { lat: -20.792486, lng: -42.894816 }, day: 1 },
        { id: 70, position: { lat: -20.793798, lng: -42.864851 }, day: 1 },
        { id: 71, position: { lat: -20.750521, lng: -42.875487 }, day: 1 },
        { id: 72, position: { lat: -20.774273, lng: -42.906006 }, day: 1 },
        { id: 73, position: { lat: -20.764686, lng: -42.900156 }, day: 1 },
        { id: 74, position: { lat: -20.758245, lng: -42.874747 }, day: 1 },
        { id: 75, position: { lat: -20.740886, lng: -42.900364 }, day: 1 }
      ];
      this.lockers = [
        {
          id: 76,
          position: { lat: -20.725772531661, lng: -42.8774070739746 },
          day: 1
        },
        { id: 77, position: { lat: -20.764141, lng: -42.854886 }, day: 1 },
        {
          id: 78,
          position: { lat: -20.7705599940022, lng: -42.8950881958008 },
          day: 1
        },
        { id: 79, position: { lat: -20.749308, lng: -42.889199 }, day: 1 },
        { id: 80, position: { lat: -20.744994, lng: -42.863478 }, day: 1 }
      ];
      this.numberOfLockers = this.lockers.length;
      this.numberOfCustomers = this.customers.length;
      this.numberOfDays = 1;
    }
  }
};
</script>
