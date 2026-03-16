<template>
  <div class="publish">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>发布二手书</span>
        </div>
      </template>
      
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="书名" prop="title">
          <el-input v-model="form.title" placeholder="请输入书名" size="large" />
        </el-form-item>
        
        <el-form-item label="作者" prop="author">
          <el-input v-model="form.author" placeholder="请输入作者" size="large" />
        </el-form-item>
        
        <el-form-item label="ISBN" prop="isbn">
          <el-input v-model="form.isbn" placeholder="请输入ISBN" size="large" />
        </el-form-item>
        
        <el-form-item label="分类" prop="category">
          <el-select v-model="form.category" placeholder="请选择分类" size="large" style="width: 100%">
            <el-option label="教材类" value="教材类" />
            <el-option label="考研资料" value="考研资料" />
            <el-option label="课外阅读" value="课外阅读" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="成色" prop="condition">
          <el-select v-model="form.condition" placeholder="请选择成色" size="large" style="width: 100%">
            <el-option label="全新" value="全新" />
            <el-option label="九成新" value="九成新" />
            <el-option label="八成新" value="八成新" />
            <el-option label="七成新" value="七成新" />
            <el-option label="及以下" value="及以下" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="价格" prop="price">
          <el-input-number
            v-model="form.price"
            :min="0.01"
            :precision="2"
            :step="0.1"
            size="large"
            style="width: 100%"
            placeholder="请输入售价"
          />
        </el-form-item>
        
        <el-form-item label="库存" prop="stock">
          <el-input-number
            v-model="form.stock"
            :min="1"
            size="large"
            style="width: 100%"
            placeholder="请输入库存数量"
          />
        </el-form-item>
        
        <el-form-item label="交易方式" prop="delivery_type">
          <el-select v-model="form.delivery_type" placeholder="请选择交易方式" size="large" style="width: 100%">
            <el-option label="仅自提" value="仅自提" />
            <el-option label="仅快递" value="仅快递" />
            <el-option label="自提+快递" value="自提+快递" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="书籍描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            placeholder="请输入书籍描述"
            size="large"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" size="large" :loading="loading" @click="handleSubmit">
            发布
          </el-button>
          <el-button size="large" @click="formRef?.resetFields()">
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { createBook } from '../api/book'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  title: '',
  author: '',
  isbn: '',
  category: '',
  condition: '',
  price: 0,
  stock: 1,
  delivery_type: '',
  description: '',
  images: []
})

const rules = {
  title: [{ required: true, message: '请输入书名', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
  condition: [{ required: true, message: '请选择成色', trigger: 'change' }],
  price: [{ required: true, message: '请输入价格', trigger: 'blur' }],
  delivery_type: [{ required: true, message: '请选择交易方式', trigger: 'change' }]
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await createBook(form)
    ElMessage.success('发布成功')
    router.push('/')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.publish {
  max-width: 800px;
  margin: 0 auto;
}

.card-header {
  font-size: 18px;
  font-weight: bold;
}
</style>
