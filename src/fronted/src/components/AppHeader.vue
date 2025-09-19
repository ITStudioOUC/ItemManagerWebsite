<template>
  <el-header class="app-header">
    <div class="header-content">
      <h1 class="logo">爱特工作室物品管理系统</h1>
      <el-menu
          mode="horizontal"
          :default-active="$route.path"
          router
          class="nav-menu"
      >
        <el-menu-item index="/">
          <el-icon><House /></el-icon>
          首页
        </el-menu-item>
        <el-menu-item index="/items">
          <el-icon><Box /></el-icon>
          物品管理
        </el-menu-item>
        <el-menu-item index="/usage">
          <el-icon><Document /></el-icon>
          使用记录
        </el-menu-item>
      </el-menu>
    </div>
  </el-header>
</template>

<script>
export default {
  name: 'AppHeader'
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
  justify-content: space-between;
  width: 100%;
}

.logo {
  color: #409eff;
  font-size: 20px;
  font-weight: bold;
  margin: 0;
}

.nav-menu {
  border-bottom: none;
  width: 60%;
  background-color: transparent;
}

.nav-menu .el-menu-item {
  border-bottom: none;
  height: 60px;
  line-height: 60px;
}
</style>
