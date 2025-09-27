<template>
  <el-header class="app-header">
    <div class="header-content">
      <div class="left-wrap">
        <el-button type="text" class="menu-toggle mobile-only" @click="drawerVisible = true" aria-label="打开导航">
          <el-icon><Menu /></el-icon>
        </el-button>
        <h1 class="logo">爱特工作室管理系统</h1>
      </div>
      <el-menu
          mode="horizontal"
          :default-active="$route.path"
          router
          class="nav-menu"
      >
        <el-menu-item index="/">
          <el-icon><House /></el-icon>
          物品统计
        </el-menu-item>
        <el-menu-item index="/items">
          <el-icon><Box /></el-icon>
          物品管理
        </el-menu-item>
        <el-menu-item index="/usage">
          <el-icon><Document /></el-icon>
          使用记录
        </el-menu-item>
        <el-menu-item index="/personnel">
          <el-icon><User /></el-icon>
          人员管理
        </el-menu-item>
        <el-menu-item index="/department-management">
          <el-icon><OfficeBuilding /></el-icon>
          部门管理
        </el-menu-item>
        <el-menu-item index="/finance">
          <el-icon><Money /></el-icon>
          财务管理
        </el-menu-item>
        <el-menu-item index="/finance/records">
          <el-icon><Tickets /></el-icon>
          财务记录
        </el-menu-item>
        <el-menu-item index="/memo">
          <el-icon><EditPen /></el-icon>
          备忘录
        </el-menu-item>
      </el-menu>
      <div class="header-actions">
        <el-button type="text" class="settings-btn" @click="goToSettings" aria-label="设置">
          <el-icon><Setting /></el-icon>
        </el-button>
      </div>
    </div>

    <!-- 移动端抽屉导航 -->
    <el-drawer v-model="drawerVisible" title="导航" size="80%" :with-header="true">
      <el-menu
        mode="vertical"
        :default-active="$route.path"
        router
        class="mobile-menu"
        @select="drawerVisible = false"
      >
        <el-menu-item index="/">
          <el-icon><House /></el-icon>
          物品统计
        </el-menu-item>
        <el-menu-item index="/items">
          <el-icon><Box /></el-icon>
          物品管理
        </el-menu-item>
        <el-menu-item index="/usage">
          <el-icon><Document /></el-icon>
          使用记录
        </el-menu-item>
        <el-menu-item index="/personnel">
          <el-icon><User /></el-icon>
          人员管理
        </el-menu-item>
        <el-menu-item index="/department-management">
          <el-icon><OfficeBuilding /></el-icon>
          部门管理
        </el-menu-item>
        <el-menu-item index="/finance">
          <el-icon><Money /></el-icon>
          财务管理
        </el-menu-item>
        <el-menu-item index="/finance/records">
          <el-icon><Tickets /></el-icon>
          财务记录
        </el-menu-item>
        <el-menu-item index="/memo">
          <el-icon><EditPen /></el-icon>
          备忘录
        </el-menu-item>
      </el-menu>
    </el-drawer>
  </el-header>
</template>

<script>
import {Box, Document, House, Money, OfficeBuilding, Setting, Tickets, User, Menu, EditPen} from '@element-plus/icons-vue'

export default {
  name: 'AppHeader',
  components: {
    House,
    Box,
    Document,
    Money,
    Tickets,
    Setting,
    User,
    OfficeBuilding,
    Menu,
    EditPen
  },
  data() {
    return {
      drawerVisible: false
    }
  },
  methods: {
    goToSettings() {
      this.$router.push('/settings')
    }
  }
}
</script>

<style scoped>
.app-header {
  background-color: #ffffff;
  box-shadow: 0 2px 4px rgba(0,0,0,.12), 0 0 6px rgba(0,0,0,.04);
  height: 60px !important;
  display: flex;
  align-items: center;
  padding: 0 20px;
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header-content {
  display: flex;
  align-items: center;
  width: 100%;
  position: relative;
}

.left-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
}

.menu-toggle {
  display: none;
  color: #606266;
  font-size: 18px;
  padding: 10px;
}

.logo {
  color: #409eff;
  font-size: 20px;
  font-weight: bold;
  margin: 0;
  position: absolute;
  left: 0;
  z-index: 1;
}

.nav-menu {
  border-bottom: none;
  background-color: transparent;
  width: 100%;
  display: flex;
  justify-content: center;
  position: absolute;
  left: 0;
  right: 0;
}

.nav-menu .el-menu-item {
  border-bottom: none;
  height: 60px;
  line-height: 60px;
}

.header-actions {
  position: absolute;
  right: 0;
  z-index: 2;
}

.settings-btn {
  color: #606266;
  font-size: 16px;
  padding: 10px;
}

.settings-btn:hover {
  color: #409eff;
}

/* 移动端/平板端样式覆盖，避免标题、菜单与设置按钮堆叠 */
@media (max-width: 1500px) {
  .app-header {
    height: auto !important;
    padding: 8px 12px;
  }
  .header-content {
    position: static;
    justify-content: space-between;
  }
  .logo {
    position: static;
    font-size: 16px;
    max-width: 60vw;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .nav-menu {
    display: none !important;
  }
  .menu-toggle {
    display: inline-flex;
  }
  .header-actions {
    position: static;
  }
}
</style>
