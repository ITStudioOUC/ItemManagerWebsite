import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
apiClient.interceptors.request.use(
  config => {
    console.log('API请求:', config.method?.toUpperCase(), config.url)
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  response => {
    console.log('API响应:', response.status, response.config.url)
    return response
  },
  error => {
    console.error('API错误:', error.response?.status, error.response?.data)
    return Promise.reject(error)
  }
)

export const itemService = {
  // 获取所有物品
  getAllItems() {
    return apiClient.get('/items/')
  },

  // 获取物品详情
  getItemDetail(id) {
    return apiClient.get(`/items/${id}/`)
  },

  // 创建新物品
  createItem(item) {
    return apiClient.post('/items/', item)
  },

  // 更新物品
  updateItem(id, item) {
    return apiClient.put(`/items/${id}/`, item)
  },

  // 删除物品
  deleteItem(id) {
    return apiClient.delete(`/items/${id}/`)
  },

  // 获取可用物品
  getAvailableItems() {
    return apiClient.get('/items/available/')
  },

  // 获取使用中的物品
  getItemsInUse() {
    return apiClient.get('/items/in_use/')
  },

  // 借用物品
  borrowItem(itemId, borrowData) {
    return apiClient.post(`/items/${itemId}/borrow/`, borrowData)
  },

  // 归还物品
  returnItem(itemId, returnData) {
    return apiClient.post(`/items/${itemId}/return_item/`, returnData)
  }
}

export const usageService = {
  // 获取所有使用记录
  getAllUsages() {
    return apiClient.get('/usages/')
  },

  // 获取当前使用中的记录
  getCurrentUsages() {
    return apiClient.get('/usages/current/')
  },

  // 根据用户获取使用记录
  getUserUsages(userId) {
    return apiClient.get(`/usages/by_user/?user_id=${userId}`)
  },

  // 创建使用记录
  createUsage(usage) {
    return apiClient.post('/usages/', usage)
  },

  // 更新使用记录
  updateUsage(id, usage) {
    return apiClient.put(`/usages/${id}/`, usage)
  }
}

export const categoryService = {
  // 获取所有类别
  getAllCategories() {
    return apiClient.get('/categories/')
  },

  // 创建新类别
  createCategory(category) {
    return apiClient.post('/categories/', category)
  },

  // 更新类别
  updateCategory(id, category) {
    return apiClient.put(`/categories/${id}/`, category)
  },

  // 删除类别
  deleteCategory(id) {
    return apiClient.delete(`/categories/${id}/`)
  }
}

export const userService = {
  // 获取所有用户
  getAllUsers() {
    return apiClient.get('/users/')
  }
}

// 健康检查API
export const healthService = {
  checkBackendConnection() {
    return apiClient.get('/items/')
  }
}

export default apiClient
