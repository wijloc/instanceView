import Vue from "vue";
import VueRouter from "vue-router";
import Map from "../components/Map.vue";

Vue.use(VueRouter);

const routes = [
  {
    path: "/",
    component: Map
  }
];

const router = new VueRouter({
  mode: "history",
  base: process.env.BASE_URL,
  routes
});

export default router;
