import {createRouter, createWebHistory} from 'vue-router'
import Login from '../views/Login.vue'
import ItemList from '../views/ItemList.vue'
import ItemDetail from '../views/ItemDetail.vue'
import ItemCreate from '../views/ItemCreate.vue'
import ItemUsage from '../views/ItemUsage.vue'
import Dashboard from '../views/Dashboard.vue'
import FinanceDashboard from '../views/FinanceDashboard.vue'
import FinanceRecordList from '../views/FinanceRecordList.vue'
import FinanceRecordDetail from '../views/FinanceRecordDetail.vue'
import PersonnelList from '../views/PersonnelList.vue'
import DepartmentProjectGroupManagement from '../views/DepartmentProjectGroupManagement.vue'
import Settings from '../views/Settings.vue'
import Memo from '../views/Memo.vue'
import EvaluationRecordList from '../views/EvaluationRecordList.vue'
import { authService } from '@/services/api'

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
    path: '/items/create',
    name: 'ItemCreate',
    component: ItemCreate
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
  },
  {
    path: '/finance',
    name: 'FinanceDashboard',
    component: FinanceDashboard
  },
  {
    path: '/finance/records',
    name: 'FinanceRecordList',
    component: FinanceRecordList
  },
  {
    path: '/finance/records/:id',
    name: 'FinanceRecordDetail',
    component: FinanceRecordDetail,
    props: true
  },
  {
    path: '/personnel',
    name: 'PersonnelList',
    component: PersonnelList
  },
  {
    path: '/department-management',
    name: 'DepartmentProjectGroupManagement',
    component: DepartmentProjectGroupManagement
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings
  },
  {
    path: '/memo',
    name: 'Memo',
    component: Memo
  },
  {
    path: '/evaluations',
    name: 'EvaluationRecordList',
    component: EvaluationRecordList
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  // 允许直接访问登录页
  if (to.path === '/login') {
    if (authService.isAuthenticated()) {
      // 已登录，跳转到首页或原定路径
      const redirect = to.query.redirect || '/'
      return next(redirect)
    }
    return next()
  }

  // 其他页面需要登录
  if (!authService.isAuthenticated()) {
    return next({ path: '/login', query: { redirect: to.fullPath } })
  }

  next()
})

export default router
