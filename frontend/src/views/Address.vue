<template>
  <div class="address">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>收货地址管理</span>
          <el-button type="primary" @click="handleAdd">新增地址</el-button>
        </div>
      </template>
      
      <div v-loading="loading">
        <el-empty v-if="addresses.length === 0 && !loading" description="暂无收货地址" />
        
        <div v-else class="address-list">
          <el-card class="address-item" v-for="item in addresses" :key="item.id">
            <div class="address-info">
              <div class="receiver">
                {{ item.receiver }}
                <el-tag size="small" style="margin-left: 10px">{{ item.phone }}</el-tag>
                <el-tag v-if="item.is_default" size="small" type="danger" style="margin-left: 10px">默认</el-tag>
              </div>
              <p class="address">{{ item.address }}</p>
            </div>
            <div class="address-actions">
              <el-button v-if="!item.is_default" size="small" @click="handleSetDefault(item.id)">设为默认</el-button>
              <el-button size="small" @click="handleEdit(item)">编辑</el-button>
              <el-button size="small" type="danger" @click="handleDelete(item.id)">删除</el-button>
            </div>
          </el-card>
        </div>
      </div>
    </el-card>
    
    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑地址' : '新增地址'"
      width="500px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="收货人" prop="receiver">
          <el-input v-model="form.receiver" placeholder="请输入收货人" size="large" />
        </el-form-item>
        <el-form-item label="电话" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入电话" size="large" />
        </el-form-item>
        <el-form-item label="地址" prop="address">
          <el-input
            v-model="form.address"
            type="textarea"
            :rows="3"
            placeholder="请输入详细地址"
            size="large"
          />
        </el-form-item>
        <el-form-item label="设为默认" prop="is_default">
          <el-switch v-model="form.is_default" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAddresses, createAddress, updateAddress, deleteAddress, setDefaultAddress } from '../api/address'

const loading = ref(false)
const submitLoading = ref(false)
const addresses = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)

const form = reactive({
  id: null,
  receiver: '',
  phone: '',
  address: '',
  is_default: 0
})

const rules = {
  receiver: [{ required: true, message: '请输入收货人', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入电话', trigger: 'blur' }],
  address: [{ required: true, message: '请输入地址', trigger: 'blur' }]
}

const fetchAddresses = async () => {
  loading.value = true
  try {
    const res = await getAddresses()
    addresses.value = res.data
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  isEdit.value = false
  Object.assign(form, {
    id: null,
    receiver: '',
    phone: '',
    address: '',
    is_default: 0
  })
  dialogVisible.value = true
}

const handleEdit = (item) => {
  isEdit.value = true
  Object.assign(form, item)
  dialogVisible.value = true
}

const handleSetDefault = async (id) => {
  try {
    await setDefaultAddress(id)
    ElMessage.success('设置成功')
    fetchAddresses()
  } catch {
    ElMessage.error('设置失败')
  }
}

const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除该地址吗？', '提示')
    await deleteAddress(id)
    ElMessage.success('删除成功')
    fetchAddresses()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitLoading.value = true
  try {
    if (isEdit.value) {
      await updateAddress(form.id, form)
    } else {
      await createAddress(form)
    }
    ElMessage.success(isEdit.value ? '更新成功' : '添加成功')
    dialogVisible.value = false
    fetchAddresses()
  } finally {
    submitLoading.value = false
  }
}

onMounted(() => {
  fetchAddresses()
})
</script>

<style scoped>
.address {
  max-width: 800px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
  font-weight: bold;
}

.address-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.address-item {
  cursor: pointer;
}

.address-info {
  margin-bottom: 10px;
}

.receiver {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
}

.address {
  color: #666;
  line-height: 1.6;
}

.address-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}
</style>
