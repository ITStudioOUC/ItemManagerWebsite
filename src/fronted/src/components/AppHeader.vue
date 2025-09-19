<template>
  <el-header class="app-header">
    <div class="header-content">
      <h1 class="logo">爱特工作室物品管理及财务管理系统</h1>
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
        <el-menu-item index="/finance">
          <el-icon><Money /></el-icon>
          财务管理
        </el-menu-item>
        <el-menu-item index="/finance/records">
          <el-icon><Tickets /></el-icon>
          财务记录
        </el-menu-item>
      </el-menu>
    </div>
  </el-header>
</template>

<script>
import { House, Box, Document, Money, Tickets } from '@element-plus/icons-vue'

export default {
  name: 'AppHeader',
  components: {
    House,
    Box,
    Document,
    Money,
    Tickets
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
</style>
