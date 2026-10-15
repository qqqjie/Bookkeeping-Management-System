<template>
  <div class="login-page">
    <el-card class="login-card">
      <h2 class="title">个人记账管理系统</h2>
      <el-tabs v-model="activeTab" stretch>
        <el-tab-pane label="登录" name="login">
          <el-form
            ref="loginFormRef"
            :model="loginForm"
            :rules="loginRules"
            size="large"
            @keyup.enter="onLogin"
          >
            <el-form-item prop="loginId">
              <el-input v-model="loginForm.loginId" placeholder="用户名或邮箱" :prefix-icon="User" />
            </el-form-item>
            <el-form-item prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="密码"
                :prefix-icon="Lock"
                show-password
              />
            </el-form-item>
            <el-button type="primary" class="submit" :loading="loading" @click="onLogin">
              登 录
            </el-button>
          </el-form>
        </el-tab-pane>
        <el-tab-pane label="注册" name="register">
          <el-form
            ref="registerFormRef"
            :model="registerForm"
            :rules="registerRules"
            size="large"
            @keyup.enter="onRegister"
          >
            <el-form-item prop="username">
              <el-input v-model="registerForm.username" placeholder="用户名（字母/数字/下划线，3-50 位）" :prefix-icon="User" />
            </el-form-item>
            <el-form-item prop="email">
              <el-input v-model="registerForm.email" placeholder="邮箱" :prefix-icon="Message" />
            </el-form-item>
            <el-form-item prop="password">
              <el-input
                v-model="registerForm.password"
                type="password"
                placeholder="密码（8-64 位，须含字母和数字）"
                :prefix-icon="Lock"
                show-password
              />
            </el-form-item>
            <el-form-item prop="nickname">
              <el-input v-model="registerForm.nickname" placeholder="昵称（选填）" :prefix-icon="Postcard" />
            </el-form-item>
            <el-button type="primary" class="submit" :loading="loading" @click="onRegister">
              注 册
            </el-button>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Lock, Message, Postcard, User } from '@element-plus/icons-vue'
import { authApi } from '@/api/auth'
import { authStore } from '@/stores/auth'

const router = useRouter()
const activeTab = ref('login')
const loading = ref(false)
const loginFormRef = ref(null)
const registerFormRef = ref(null)

const loginForm = reactive({ loginId: '', password: '' })
const registerForm = reactive({ username: '', email: '', password: '', nickname: '' })

const loginRules = {
  loginId: [{ required: true, message: '请输入用户名或邮箱', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    {
      pattern: /^[a-zA-Z0-9_]{3,50}$/,
      message: '只能包含字母、数字、下划线，长度 3-50',
      trigger: 'blur'
    }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    {
      pattern: /^[^@\s]+@[^@\s]+\.[^@\s]+$/,
      message: '邮箱格式不正确',
      trigger: 'blur'
    }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, max: 64, message: '密码长度必须在 8-64 之间', trigger: 'blur' },
    {
      pattern: /^(?=.*[a-zA-Z])(?=.*\d).+$/,
      message: '密码必须同时包含字母和数字',
      trigger: 'blur'
    }
  ],
  nickname: [{ max: 50, message: '昵称长度不能超过 50', trigger: 'blur' }]
}

function afterAuth(response, welcomeText) {
  authStore.setAuth(response.token, response.user)
  ElMessage.success(welcomeText)
  router.push('/')
}

async function onLogin() {
  await loginFormRef.value.validate()
  loading.value = true
  try {
    const data = await authApi.login({
      loginId: loginForm.loginId.trim(),
      password: loginForm.password
    })
    afterAuth(data, '登录成功')
  } finally {
    loading.value = false
  }
}

async function onRegister() {
  await registerFormRef.value.validate()
  loading.value = true
  try {
    const data = await authApi.register({
      username: registerForm.username.trim(),
      email: registerForm.email.trim(),
      password: registerForm.password,
      nickname: registerForm.nickname.trim() || undefined
    })
    afterAuth(data, '注册成功，已自动登录')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%);
}

.login-card {
  width: 400px;
  padding: 12px;
}

.title {
  text-align: center;
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 12px;
}

.submit {
  width: 100%;
}
</style>
