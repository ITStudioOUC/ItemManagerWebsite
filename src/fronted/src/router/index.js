import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import ItemList from '../views/ItemList.vue'
import ItemDetail from '../views/ItemDetail.vue'
import ItemUsage from '../views/ItemUsage.vue'
import Dashboard from '../views/Dashboard.vue'

const routes = [
  {
    path: "/login",
    name: 'Login',
    component: Login,
  },
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard
  },
  {
    path: '/items',
    name: 'ItemList',
    component: ItemList
  },
  {
    path: '/items/:id',
    name: 'ItemDetail',
    component: ItemDetail,
    props: true
  },
  {
    path: '/usage',
    name: 'ItemUsage',
    component: ItemUsage
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
