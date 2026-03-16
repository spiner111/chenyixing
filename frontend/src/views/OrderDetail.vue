<template>
  <div class="order-detail" v-loading="loading">
    <el-page-header @back="goBack" content="返回订单列表" />
    
    <div v-if="order">
      <!-- 订单信息 -->
      <el-card class="info-card">
        <div class="order-status">
          <el-icon :size="40" :color="getStatusColor(order.status)"><CircleCheck /></el-icon>
          <div class="status-text">
            <h2>{{ order.status_text }}</h2>
            <p>订单号：{{ order.order_no }}</p>
            <p>创建时间：{{ order.created_at }}</p>
          </div>
        </div>
      </el-card>
      
      <!-- 商品信息 -->
      <el-card class="info-card" style="margin-top: 20px">
        <template #header>
          <span>商品信息</span>
        </template>
        <div class="book-info">
          <el-image
            :src="order.book_image || '/default-book.png'"
            fit="cover"
            style="width: 120px; height: 120px; border-radius: 8px"
          />
          <div class="book-details">
            <h3>{{ order.book_title }}</h3>
            <p class="price">¥{{ order.total_price }}</p>
          </div>
        </div>
      </el-card>
      
      <!-- 收货地址 -->
      <el-card class="info-card" style="margin-top: 20px">
        <template #header>
          <span>收货地址</span>
        </template>
        <div class="address-info">
          <el-icon :size="24" color="#409eff"><Location /></el-icon>
          <div class="address-details">
            <div class="receiver">
              {{ order.receiver }}
              <el-tag size="small" style="margin-left: 10px">{{ order.phone }}</el-tag>
            </div>
            <p class="address">{{ order.address }}</p>
          </div>
        </div>
      </el-card>
      
      <!-- 操作按钮 -->
      <div class="action-buttons" style="margin-top: 20px">
        <el-button v-if="order.status === 1" type="danger" size="large" @click="handleCancel">
          取消订单
        </el-button>
        <el-button v-if="order.status === 1" type="primary" size="large" @click="handlePay">
          立即付款
        </el-button>
        <el-button v-if="order.status === 3" type="success" size="large" @click="handleConfirm">
          确认收货
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getOrderDetail, cancelOrder, payOrder, confirmOrder } from '../api/order'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const order = ref(null)

const fetchOrder = async () => {
  loading.value = true
  try {
    const res = await getOrderDetail(route.params.id)
    order.value = res.data
  } finally {
    loading.value = false
  }
}

const getStatusColor = (status) => {
  const map = {
    0: '#909399',
    1: '#e6a23c',
    2: '#409eff',
    3: '#67c23a',
    4: '#67c23a'
  }
  return map[status] || '#909399'
}

const handleCancel = async () => {
  try {
    await ElMessageBox.confirm('确定要取消订单吗？', '提示')
    await cancelOrder(order.value.id)
    ElMessage.success('订单已取消')
    fetchOrder()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('取消失败')
    }
  }
}

const handlePay = async () => {
  try {
    await ElMessageBox.confirm('确定要支付订单吗？（模拟支付）', '提示')
    await payOrder(order.value.id)
    ElMessage.success('支付成功')
    fetchOrder()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('支付失败')
    }
  }
}

const handleConfirm = async () => {
  try {
    await ElMessageBox.confirm('确定已收到商品吗？', '提示')
    await confirmOrder(order.value.id)
    ElMessage.success('确认收货成功')
    fetchOrder()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('确认收货失败')
    }
  }
}

const goBack = () => {
  router.back()
}

onMounted(() => {
  fetchOrder()
})
</script>

<style scoped>
.order-detail {
  max-width: 800px;
  margin: 0 auto;
}

.info-card {
  margin-top: 20px;
}

.order-status {
  display: flex;
  gap: 20px;
  align-items: center;
}

.status-text h2 {
  margin-bottom: 10px;
  color: #333;
}

.status-text p {
  color: #999;
  font-size: 14px;
  margin: 5px 0;
}

.book-info {
  display: flex;
  gap: 20px;
  align-items: center;
}

.book-details h3 {
  margin-bottom: 15px;
  font-size: 18px;
}

.book-details .price {
  color: #f56c6c;
  font-size: 24px;
  font-weight: bold;
}

.address-info {
  display: flex;
  gap: 15px;
  align-items: flex-start;
}

.address-details .receiver {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
}

.address-details .address {
  color: #666;
  line-height: 1.6;
}

.action-buttons {
  display: flex;
  gap: 15px;
  justify-content: center;
}
</style>
