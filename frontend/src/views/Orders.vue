<template>
  <div class="orders">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>我的订单</span>
        </div>
      </template>
      
      <!-- 状态筛选 -->
      <el-radio-group v-model="status" @change="handleStatusChange" style="margin-bottom: 20px">
        <el-radio-button label="">全部</el-radio-button>
        <el-radio-button :label="1">待付款</el-radio-button>
        <el-radio-button :label="2">待发货</el-radio-button>
        <el-radio-button :label="3">待收货</el-radio-button>
        <el-radio-button :label="4">已完成</el-radio-button>
        <el-radio-button :label="0">已取消</el-radio-button>
      </el-radio-group>
      
      <!-- 订单列表 -->
      <div v-loading="loading">
        <el-empty v-if="orders.length === 0 && !loading" description="暂无订单" />
        
        <el-timeline v-else>
          <el-timeline-item v-for="order in orders" :key="order.id">
            <el-card class="order-card" @click="goToDetail(order.id)">
              <div class="order-header">
                <span class="order-no">订单号：{{ order.order_no }}</span>
                <el-tag :type="getStatusType(order.status)">{{ order.status_text }}</el-tag>
              </div>
              <div class="order-content">
                <div class="book-info">
                  <el-image
                    :src="order.book_image || '/default-book.png'"
                    fit="cover"
                    style="width: 80px; height: 80px; border-radius: 4px"
                  />
                  <div class="book-details">
                    <h4>{{ order.book_title }}</h4>
                    <p class="price">¥{{ order.total_price }}</p>
                  </div>
                </div>
                <div class="order-actions" @click.stop>
                  <el-button v-if="order.status === 1" type="danger" size="small" @click="handleCancel(order.id)">
                    取消订单
                  </el-button>
                  <el-button v-if="order.status === 1" type="primary" size="small" @click="handlePay(order.id)">
                    立即付款
                  </el-button>
                  <el-button v-if="order.status === 3" type="success" size="small" @click="handleConfirm(order.id)">
                    确认收货
                  </el-button>
                  <el-button size="small" @click="goToDetail(order.id)">
                    查看详情
                  </el-button>
                </div>
              </div>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </div>
      
      <!-- 分页 -->
      <div class="pagination" v-if="total > 0">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="perPage"
          :total="total"
          layout="prev, pager, next"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getOrders, cancelOrder, payOrder, confirmOrder } from '../api/order'

const router = useRouter()
const loading = ref(false)
const orders = ref([])
const page = ref(1)
const perPage = ref(20)
const total = ref(0)
const status = ref('')

const fetchOrders = async () => {
  loading.value = true
  try {
    const params = {
      page: page.value,
      per_page: perPage.value
    }
    if (status !== '') {
      params.status = status.value
    }
    const res = await getOrders(params)
    orders.value = res.data.orders
    total.value = res.data.total
  } finally {
    loading.value = false
  }
}

const getStatusType = (status) => {
  const map = {
    0: 'info',
    1: 'warning',
    2: 'primary',
    3: 'success',
    4: ''
  }
  return map[status] || ''
}

const handleStatusChange = () => {
  page.value = 1
  fetchOrders()
}

const handlePageChange = (newPage) => {
  page.value = newPage
  fetchOrders()
}

const handleCancel = async (id) => {
  try {
    await ElMessageBox.confirm('确定要取消订单吗？', '提示')
    await cancelOrder(id)
    ElMessage.success('订单已取消')
    fetchOrders()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('取消失败')
    }
  }
}

const handlePay = async (id) => {
  try {
    await ElMessageBox.confirm('确定要支付订单吗？（模拟支付）', '提示')
    await payOrder(id)
    ElMessage.success('支付成功')
    fetchOrders()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('支付失败')
    }
  }
}

const handleConfirm = async (id) => {
  try {
    await ElMessageBox.confirm('确定已收到商品吗？', '提示')
    await confirmOrder(id)
    ElMessage.success('确认收货成功')
    fetchOrders()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('确认收货失败')
    }
  }
}

const goToDetail = (id) => {
  router.push(`/order/${id}`)
}

onMounted(() => {
  fetchOrders()
})
</script>

<style scoped>
.orders {
  max-width: 1000px;
  margin: 0 auto;
}

.card-header {
  font-size: 18px;
  font-weight: bold;
}

.order-card {
  margin-bottom: 15px;
  cursor: pointer;
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.order-no {
  color: #999;
  font-size: 14px;
}

.order-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.book-info {
  display: flex;
  gap: 15px;
  align-items: center;
}

.book-details h4 {
  margin-bottom: 8px;
  font-size: 16px;
}

.book-details .price {
  color: #f56c6c;
  font-size: 18px;
  font-weight: bold;
}

.order-actions {
  display: flex;
  gap: 10px;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
</style>
