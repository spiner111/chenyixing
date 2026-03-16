<template>
  <div class="book-detail" v-loading="loading">
    <el-page-header @back="goBack" content="返回列表" />
    
    <div class="detail-content" v-if="book">
      <el-row :gutter="30">
        <!-- 左侧图片 -->
        <el-col :xs="24" :md="10">
          <el-image
            :src="book.images[0] || '/default-book.png'"
            fit="cover"
            style="width: 100%; height: 400px; border-radius: 8px"
          >
            <template #error>
              <div class="image-placeholder">
                <el-icon :size="80"><Picture /></el-icon>
              </div>
            </template>
          </el-image>
        </el-col>
        
        <!-- 右侧信息 -->
        <el-col :xs="24" :md="14">
          <h1 class="book-title">{{ book.title }}</h1>
          <div class="book-tags">
            <el-tag size="large">{{ book.category }}</el-tag>
            <el-tag size="large" type="info">{{ book.condition }}</el-tag>
            <el-tag size="large" type="success">{{ book.delivery_type }}</el-tag>
          </div>
          <div class="book-price">
            <span class="label">售价</span>
            <span class="price">¥{{ book.price }}</span>
          </div>
          
          <el-divider />
          
          <div class="book-info-item">
            <span class="label">作者：</span>
            <span>{{ book.author || '未知' }}</span>
          </div>
          <div class="book-info-item" v-if="book.isbn">
            <span class="label">ISBN：</span>
            <span>{{ book.isbn }}</span>
          </div>
          <div class="book-info-item">
            <span class="label">库存：</span>
            <span>{{ book.stock }} 本</span>
          </div>
          <div class="book-info-item">
            <span class="label">发布时间：</span>
            <span>{{ book.created_at }}</span>
          </div>
          
          <el-divider />
          
          <div class="book-description" v-if="book.description">
            <h3>书籍描述</h3>
            <p>{{ book.description }}</p>
          </div>
          
          <el-divider />
          
          <div class="seller-info">
            <el-avatar :size="50" :icon="UserFilled" />
            <div class="seller-details">
              <div class="seller-name">{{ book.seller }}</div>
              <div class="seller-time">发布时间：{{ book.created_at }}</div>
            </div>
          </div>
          
          <div class="action-buttons">
            <el-button
              type="primary"
              size="large"
              :disabled="book.stock < 1"
              @click="handleBuy"
            >
              立即购买
            </el-button>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getBookDetail } from '../api/book'
import { getAddresses } from '../api/address'
import { createOrder } from '../api/order'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const book = ref(null)

const fetchBook = async () => {
  loading.value = true
  try {
    const res = await getBookDetail(route.params.id)
    book.value = res.data
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.back()
}

const handleBuy = async () => {
  try {
    const res = await getAddresses()
    if (res.data.length === 0) {
      ElMessage.warning('请先添加收货地址')
      router.push('/address')
      return
    }
    
    const defaultAddress = res.data.find(a => a.is_default) || res.data[0]
    const orderRes = await createOrder({
      book_id: book.value.id,
      address_id: defaultAddress.id
    })
    ElMessage.success('订单创建成功')
    router.push(`/order/${orderRes.data.id}`)
  } catch (error) {
    ElMessage.error('购买失败')
  }
}

onMounted(() => {
  fetchBook()
})
</script>

<style scoped>
.book-detail {
  max-width: 1200px;
  margin: 0 auto;
}

.detail-content {
  margin-top: 20px;
  background: #fff;
  padding: 30px;
  border-radius: 8px;
}

.image-placeholder {
  width: 100%;
  height: 400px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f5f5;
  border-radius: 8px;
}

.book-title {
  font-size: 28px;
  margin-bottom: 15px;
  color: #333;
}

.book-tags {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.book-price {
  display: flex;
  align-items: baseline;
  gap: 10px;
  margin-bottom: 20px;
}

.book-price .label {
  font-size: 16px;
  color: #666;
}

.book-price .price {
  font-size: 32px;
  color: #f56c6c;
  font-weight: bold;
}

.book-info-item {
  margin-bottom: 10px;
  color: #666;
}

.book-info-item .label {
  color: #999;
}

.book-description {
  margin-bottom: 20px;
}

.book-description h3 {
  font-size: 16px;
  margin-bottom: 10px;
  color: #333;
}

.book-description p {
  color: #666;
  line-height: 1.6;
}

.seller-info {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
}

.seller-name {
  font-weight: bold;
  font-size: 16px;
  margin-bottom: 5px;
}

.seller-time {
  color: #999;
  font-size: 14px;
}

.action-buttons {
  display: flex;
  gap: 15px;
}
</style>
