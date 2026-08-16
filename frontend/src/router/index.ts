import { createRouter, createWebHistory } from "vue-router";
import Home from "../views/Home.vue";
import Stats from "../views/Stats.vue";
import Explorer from "../views/Explorer.vue";
import Methodology from "../views/Methodology.vue";

export default createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: "/", component: Home },
    { path: "/statistics", component: Stats },
    { path: "/explorer", component: Explorer },
    { path: "/methodology", component: Methodology },
  ],
});
