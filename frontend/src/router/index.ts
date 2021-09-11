import Vue from "vue";
import VueRouter, { RouteConfig } from "vue-router";
import Home from "../views/Home.vue";
import Stats from "../views/Stats.vue";
import Explorer from "../views/Explorer.vue";
import Methodology from "../views/Methodology.vue";

Vue.use(VueRouter);

const routes: Array<RouteConfig> = [
  {
    path: "/",
    name: "Home",
    component: Home
  },
  {
    path: "/statistics",
    name: "Stats",
    component: Stats
  },
  {
    path: "/explorer",
    name: "Explorer",
    component: Explorer
  },
  {
    path: "/methodology",
    name: "Methodology",
    component: Methodology
  },
];

const router = new VueRouter({
  mode: "history",
  base: process.env.BASE_URL,
  routes
});

export default router;
