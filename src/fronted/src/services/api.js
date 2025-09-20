import axios from 'axios'

export const API_BASE_URL = 'http://localhost:8000/api'

export const API_BASE_URL_WITHOUT_API = 'http://localhost:8000'

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

  // 根据用户姓名获取使用记录
  getUserUsages(userName) {
    return apiClient.get(`/usages/by_user/?user_name=${userName}`)
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
    return apiClient.get('/item_categories/')
  },

  // 创建新类别
  createCategory(category) {
    return apiClient.post('/item_categories/', category)
  },

  // 更新类别
  updateCategory(id, category) {
    return apiClient.put(`/item_categories/${id}/`, category)
  },

  // 删除类别
  deleteCategory(id) {
    return apiClient.delete(`/item_categories/${id}/`)
  }
}

export const userService = {
  // 获取所有用户
  getAllUsers() {
    return apiClient.get('/users/')
  }
}

export const financeService = {
    // 获取所有财务记录
    getAllFinanceRecords() {
        return apiClient.get('/finance/')
    },

    // 获取单个财务记录
    getFinanceRecord(id) {
        return apiClient.get(`/finance/${id}/`)
    },

    // 创建财务记录
    createFinanceRecord(record) {
        return apiClient.post('/finance/', record, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        })
    },

    // 更新财务记录
    updateFinanceRecord(id, record) {
        return apiClient.put(`/finance/${id}/`, record, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        })
    },

    // 删除财务记录
    deleteFinanceRecord(id) {
        return apiClient.delete(`/finance/${id}/`)
    },

    // 为财务记录上传多张凭证图片
    uploadImages(recordId, formData) {
        return apiClient.post(`/finance/${recordId}/upload_images/`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        })
    },

    // 删除凭证图片
    deleteProofImage(imageId) {
        return apiClient.delete(`/proof-images/${imageId}/`)
    },

    // 获取所有部门
    getAllDepartments() {
        return apiClient.get('/departments/')
    },

    // 创建部门
    createDepartment(department) {
        return apiClient.post('/departments/', department)
    },

    // 更新部门
    updateDepartment(id, department) {
        return apiClient.put(`/departments/${id}/`, department)
    },

    // 删除部门
    deleteDepartment(id) {
        return apiClient.delete(`/departments/${id}/`)
    },

    // 获取所有类别
    getAllCategories() {
        return apiClient.get('/finance_categories/')
    },
}

// 人员管理服务
export const personnelService = {
    // 获取所有人员
    getAllPersonnel() {
        return apiClient.get('/personnel/')
    },

    // 获取人员详情
    getPersonnelDetail(id) {
        return apiClient.get(`/personnel/${id}/`)
    },

    // 创建新人员
    createPersonnel(personnel) {
        return apiClient.post('/personnel/', personnel)
    },

    // 更新人员信息
    updatePersonnel(id, personnel) {
        return apiClient.put(`/personnel/${id}/`, personnel)
    },

    // 删除人员
    deletePersonnel(id) {
        return apiClient.delete(`/personnel/${id}/`)
    },

    // 设置人员已卸任
    setPersonnelInactive(id) {
        return apiClient.post(`/personnel/${id}/set_inactive/`)
    },

    // 设置人员在职
    setPersonnelActive(id) {
        return apiClient.post(`/personnel/${id}/set_active/`)
    },

    // 获取人员统计信息
    getPersonnelStatistics() {
        return apiClient.get('/personnel/statistics/')
    },

    // 按部门筛选人员
    getPersonnelByDepartment(departmentId) {
        return apiClient.get('/personnel/', {
            params: { department: departmentId }
        })
    },

    // 按项目组筛选人员
    getPersonnelByProjectGroup(projectGroupId) {
        return apiClient.get('/personnel/', {
            params: { project_group: projectGroupId }
        })
    },

    // 搜索人员
    searchPersonnel(keyword) {
        return apiClient.get('/personnel/', {
            params: { search: keyword }
        })
    },

    // 检查并更新到期人员状态
    checkExpiredPersonnel() {
        return apiClient.post('/personnel/check_expired/')
    }
}

// 项目组管理服务
export const projectGroupService = {
    // 获取所有项目组
    getAllProjectGroups() {
        return apiClient.get('/project-groups/')
    },

    // 获取项目组详情
    getProjectGroupDetail(id) {
        return apiClient.get(`/project-groups/${id}/`)
    },

    // 创建新项目组
    createProjectGroup(projectGroup) {
        return apiClient.post('/project-groups/', projectGroup)
    },

    // 更新项目组
    updateProjectGroup(id, projectGroup) {
        return apiClient.put(`/project-groups/${id}/`, projectGroup)
    },

    // 删除项目组
    deleteProjectGroup(id) {
        return apiClient.delete(`/project-groups/${id}/`)
    },

    // 按部门获取项目组
    getProjectGroupsByDepartment(departmentId) {
        return apiClient.get('/project-groups/by_department/', {
            params: { department_id: departmentId }
        })
    }
}

