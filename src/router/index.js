import Vue from "vue";
import VueRouter from "vue-router";
import Map from "../components/Map.vue";
import Teste from "../components/Teste.vue";

Vue.use(VueRouter);

const routes = [
  {
    path: "/",
    component: Map,
  },
  {    
    path: "/teste",
    component: Teste,
  }
];

const router = new VueRouter({
  mode: "history",
  base: process.env.BASE_URL,
  routes
});

export default router;
