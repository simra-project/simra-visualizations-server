import Vue from 'vue'
import VueRouter, { RouteConfig } from 'vue-router'
import Map from '../views/Map.vue'
import About from '../views/About.vue'

Vue.use(VueRouter)

const routes: Array<RouteConfig> = [
  {
    path: '/',
    redirect: '/map'
  },
  {
    path: '/map',
    name: 'Map',
    component: Map
  },
  {
    path: '/about',
    name: 'About',
    component: About
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
