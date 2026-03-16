<template>
  <div class="profile">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>个人中心</span>
        </div>
      </template>
      
      <div class="profile-content">
        <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
          <el-form-item label="头像">
            <el-avatar :size="100" :icon="UserFilled" :src="form.avatar" />
          </el-form-item>
          <el-form-item label="昵称" prop="nickname">
            <el-input v-model="form.nickname" placeholder="请输入昵称" size="large" />
          </el-form-item>
          <el-form-item label="用户名">
            <el-input v-model="form.username" disabled size="large" />
          </el-form-item>
          <el-form-item label="邮箱" v-if="form.email">
            <el-input v-model="form.email" disabled size="large" />
          </el-form-item>
          <el-form-item label="手机号" v-if="form.phone">
            <el-input v-model="form.phone" disabled size="large" />
          </el-form-item>
          <el-form-item label="注册时间">
            <el-input v-model="form.created_at" disabled size="large" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" size="large" :loading="loading" @click="handleSubmit">
              保存修改
            </el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getProfile, updateProfile } from '../api/user'
import { useUserStore } from '../stores/user'

const userStore = useUserStore()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  nickname: '',
  avatar: '',
  username: '',
  email: '',
  phone: '',
  created_at: ''
})

const rules = {
  nickname: [{ required: true, message: '请输入昵称', trigger: 'blur' }]
}

const fetchProfile = async () => {
  try {
    const res = await getProfile()
    Object.assign(form, res.data)
  } catch {
    ElMessage.error('获取用户信息失败')
  }
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const res = await updateProfile({
      nickname: form.nickname,
      avatar: form.avatar
    })
    userStore.setUserInfo(res.data)
    ElMessage.success('保存成功')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  Object.assign(form, userStore.userInfo)
  fetchProfile()
})
</script>

<style scoped>
.profile {
  max-width: 600px;
  margin: 0 auto;
}

.card-header {
  font-size: 18px;
  font-weight: bold;
}

.profile-content {
  padding: 20px 0;
}
</style>
