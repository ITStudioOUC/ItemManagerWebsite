/* eslint-disable */
<template>
  <div class="login-page">
    <!-- 全页面背景轮播图 -->
    <div class="background-carousel">
      <div class="carousel-overlay"></div>
      <div class="carousel-container">
        <div
          v-for="(image, index) in backgroundImages"
          :key="index"
          :class="['carousel-slide', { active: currentSlide === index }]"
          :style="{ backgroundImage: `url(${image})` }"
        ></div>
      </div>
    </div>

    <!-- Header -->
    <div class="login-header">
      <div class="header-content">
        <h1 class="system-title">爱特工作室物品管理及财务管理系统</h1>
        <div class="favicon-container">
          <img src="../../public/favicon.svg" alt="网站图标" class="favicon">
        </div>
      </div>
    </div>

    <!-- 主体内容 -->
    <div class="login-main">
      <!-- 右侧登录表单 -->
      <div class="login-form-container">
        <div class="login-form-wrapper">
          <div class="login-card">
            <div class="card-header">
              <h2>欢迎来到爱特工作室</h2>
            </div>

            <el-form
              :model="loginForm"
              :rules="formRules"
              ref="loginFormRef"
              class="login-form"
              @submit.prevent="handleLogin"
            >
              <el-form-item prop="username">
                <el-input
                  v-model="loginForm.username"
                  placeholder="账户"
                  size="large"
                  prefix-icon="User"
                  class="form-input"
                />
              </el-form-item>

              <el-form-item prop="password">
                <el-input
                  v-model="loginForm.password"
                  type="password"
                  placeholder="密码"
                  size="large"
                  prefix-icon="Lock"
                  show-password
                  class="form-input"
                  @keyup.enter="handleLogin"
                />
              </el-form-item>

              <el-form-item>
                <el-button
                  type="primary"
                  size="large"
                  class="login-button"
                  :loading="isLoading"
                  @click="handleLogin"
                >
                  {{ isLoading ? '登录中...' : '登录' }}
                </el-button>
              </el-form-item>
            </el-form>

            <!-- 网站免责说明 -->
            <div class="disclaimer">
              <p class="disclaimer-text">
                本系统仅供爱特工作室内部使用。使用本系统即表示您同意遵守相关规定，
                工作室对系统使用过程中产生的任何问题不承担法律责任。
                如有疑问，请联系管理员。
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ElMessage } from 'element-plus'

export default {
  name: 'Login',
  data() {
    return {
      loginForm: {
        username: '',
        password: ''
      },
      formRules: {
        username: [
          { required: true, message: '请输入账户', trigger: 'blur' },
          { min: 2, max: 20, message: '账户长度在 2 到 20 个字符', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
        ]
      },
      isLoading: false,
      currentSlide: 0,
      backgroundImages: [
        '../../_images/background1.jpg',
        '../../_images/background2.jpg',
      ],
      slideTimer: null
    }
  },
  mounted() {
    this.initializeCarousel()
  },
  beforeUnmount() {
    if (this.slideTimer) {
      clearInterval(this.slideTimer)
    }
  },
  methods: {
    initializeCarousel() {
      // 启动轮播定时器
      this.slideTimer = setInterval(() => {
        this.nextSlide()
      }, 5000) // 每5秒切换一张图片
    },

    nextSlide() {
      this.currentSlide = (this.currentSlide + 1) % this.backgroundImages.length
    },

    async handleLogin() {
      try {
        // 表单验证
        await this.$refs.loginFormRef.validate()

        this.isLoading = true

        // 模拟登录API调用
        await this.performLogin()

        ElMessage.success('登录成功')

        // 跳转到主页
        await this.$router.push('/')

      } catch (error) {
        console.error('登录失败:', error)
        if (error !== 'validation failed') {
          ElMessage.error('登录失败，请检查账户和密码')
        }
      } finally {
        this.isLoading = false
      }
    },

    async performLogin() {
      // 模拟API调用延迟
      return new Promise((resolve, reject) => {
        setTimeout(() => {
          // 简单的模拟验证
          if (this.loginForm.username && this.loginForm.password) {
            resolve()
          } else {
            reject(new Error('账户或密码错误'))
          }
        }, 1500)
      })
    }
  }
}
</script>

<style scoped>
/* 重置所有元素的盒模型和边距 */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html, body {
  height: 100%;
  width: 100%;
  overflow: hidden; /* 隐藏整体滚动条 */
  margin: 0;
  padding: 0;
}

.login-page {
  height: 100vh;
  width: 100vw;
  position: fixed; /* 改为fixed避免滚动 */
  top: 0;
  left: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* 全页面背景轮播图样式 */
.background-carousel {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

.carousel-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(0, 0, 0, 0.3) 0%, rgba(0, 0, 0, 0.1) 50%, rgba(0, 0, 0, 0.3) 100%);
  z-index: 2;
}

.carousel-container {
  position: relative;
  width: 100%;
  height: 100%;
}

.carousel-slide {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  opacity: 0;
  transition: opacity 2s ease-in-out;
  transform: scale(1.02); /* 减小缩放避免溢出 */
}

.carousel-slide.active {
  opacity: 1;
}

/* Header 样式优化 */
.login-header {
  position: relative;
  z-index: 100;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.12) 0%, rgba(255, 255, 255, 0.08) 100%);
  backdrop-filter: blur(15px) saturate(150%);
  border-bottom: 1px solid rgba(255, 255, 255, 0.15);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  flex-shrink: 0; /* 防止Header被压缩 */
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 30px;
  max-width: 100%;
  margin: 0 auto;
  height: 70px; /* 减小Header高度 */
}

.system-title {
  color: #ffffff;
  font-size: 24px; /* 减小字体大小 */
  font-weight: 600;
  margin: 0;
  text-shadow: 1px 1px 4px rgba(0, 0, 0, 0.3);
  letter-spacing: 0.5px;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.favicon-container {
  display: flex;
  align-items: center;
  padding: 8px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  flex-shrink: 0;
}

.favicon {
  height: 45px; /* 减小图标大小 */
  width: auto;
  filter: drop-shadow(1px 1px 2px rgba(0, 0, 0, 0.2));
}

/* 主体内容样式优化 */
.login-main {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  z-index: 10;
  padding: 0;
  overflow: hidden;
  min-height: 0; /* 允许flex收缩 */
}

/* 右侧登录表单容器优化 */
.login-form-container {
  position: relative;
  z-index: 10;
  width: 800px; /* 修复宽度 */
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 30px; /* 减小内边距 */
  overflow-y: auto; /* 允许内部滚动 */
  overflow-x: hidden;
}

.login-form-wrapper {
  width: 100%;
  max-width: 320px; /* 减小最大宽度 */
}

.login-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.85) 0%, rgba(255, 255, 255, 0.75) 100%);
  border-radius: 16px; /* 减小圆角 */
  padding: 35px 30px; /* 减小内边距 */
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.12);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.25);
  position: relative;
  overflow: hidden;
}

.login-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #1890ff 0%, #40a9ff 50%, #69c0ff 100%);
  border-radius: 16px 16px 0 0;
}

.card-header {
  text-align: center;
  margin-bottom: 30px; /* 减小间距 */
  position: relative;
}

.card-header h2 {
  color: #1890ff;
  font-size: 24px; /* 减小字体 */
  font-weight: 600;
  margin: 0;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.08);
  position: relative;
}

.card-header h2::after {
  content: '';
  position: absolute;
  bottom: -8px;
  left: 50%;
  transform: translateX(-50%);
  width: 50px;
  height: 2px;
  background: linear-gradient(90deg, #1890ff 0%, #40a9ff 100%);
  border-radius: 1px;
}

/* 表单样式优化 */
.login-form {
  margin-bottom: 25px; /* 减小间距 */
}

.form-input {
  margin-bottom: 20px; /* 减小间距 */
}

.form-input :deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.9);
  border: 1.5px solid rgba(24, 144, 255, 0.15);
  border-radius: 10px;
  padding: 12px 16px; /* 减小内边距 */
  transition: all 0.25s ease;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.08);
}

.form-input :deep(.el-input__wrapper:hover) {
  border-color: rgba(24, 144, 255, 0.4);
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.15);
  transform: translateY(-1px);
}

.form-input :deep(.el-input__wrapper.is-focus) {
  border-color: #1890ff;
  box-shadow: 0 6px 16px rgba(24, 144, 255, 0.25);
  transform: translateY(-1px);
}

.login-button {
  width: 100%;
  height: 48px; /* 减小按钮高度 */
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, #1890ff 0%, #40a9ff 50%, #69c0ff 100%);
  border: none;
  border-radius: 10px;
  transition: all 0.25s ease;
  box-shadow: 0 6px 20px rgba(24, 144, 255, 0.25);
  position: relative;
  overflow: hidden;
}

.login-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.25), transparent);
  transition: left 0.5s;
}

.login-button:hover::before {
  left: 100%;
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(24, 144, 255, 0.35);
}

.login-button:active {
  transform: translateY(0);
}

/* 免责说明样式优化 */
.disclaimer {
  margin-top: 25px; /* 减小间距 */
  padding-top: 20px;
  border-top: 1px solid rgba(24, 144, 255, 0.12);
}

.disclaimer-text {
  font-size: 11px; /* 减小字体 */
  line-height: 1.5;
  color: #666;
  text-align: center;
  margin: 0;
  background: linear-gradient(135deg, rgba(249, 249, 249, 0.85) 0%, rgba(240, 248, 255, 0.85) 100%);
  padding: 15px; /* 减小内边距 */
  border-radius: 10px;
  border-left: 3px solid #1890ff;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.08);
}

/* 响应式设计优化 */
@media (max-width: 1200px) {
  .login-form-container {
    width: 380px;
    padding: 25px;
  }
}

@media (max-width: 768px) {
  .login-form-container {
    width: 100%;
    padding: 20px 15px;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.3) 0%, rgba(255, 255, 255, 0.2) 100%);
  }

  .system-title {
    font-size: 18px;
  }

  .header-content {
    padding: 12px 20px;
    height: 60px;
  }

  .login-card {
    padding: 30px 20px;
  }

  .favicon {
    height: 38px;
  }
}

@media (max-width: 480px) {
  .login-form-container {
    padding: 15px 10px;
  }

  .login-card {
    padding: 25px 18px;
  }

  .card-header h2 {
    font-size: 20px;
  }

  .system-title {
    font-size: 14px;
  }

  .header-content {
    padding: 8px 15px;
    height: 50px;
  }

  .favicon {
    height: 32px;
  }
}

/* 动画效果优化 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.login-card {
  animation: fadeInUp 0.6s ease-out;
}

.carousel-slide {
  animation: slideZoom 25s ease-in-out infinite;
}

@keyframes slideZoom {
  0%, 100% {
    transform: scale(1.02);
  }
  50% {
    transform: scale(1.05);
  }
}

/* 滚动条样式 */
.login-form-container::-webkit-scrollbar {
  width: 4px;
}

.login-form-container::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
}

.login-form-container::-webkit-scrollbar-thumb {
  background: rgba(24, 144, 255, 0.3);
  border-radius: 2px;
}

.login-form-container::-webkit-scrollbar-thumb:hover {
  background: rgba(24, 144, 255, 0.5);
}
</style>
