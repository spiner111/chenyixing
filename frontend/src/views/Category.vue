<template>
  <div class="category">
    <el-page-header @back="goBack" :content="`${categoryName}书籍`" />
    
    <div class="book-list" v-loading="loading">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="book in books" :key="book.id">
          <el-card class="book-card" @click="goToDetail(book.id)">
            <div class="book-image">
              <el-image
                :src="book.images[0] || '/default-book.png'"
                fit="cover"
                style="width: 100%; height: 200px"
              >
                <template #error>
                  <div class="image-placeholder">
                    <el-icon :size="50"><Picture /></el-icon>
                  </div>
                </template>
              </el-image>
            </div>
            <div class="book-info">
              <h3 class="book-title">{{ book.title }}</h3>
              <p class="book-author">{{ book.author || '未知作者' }}</p>
              <div class="book-meta">
                <el-tag size="small">{{ book.category }}</el-tag>
                <el-tag size="small" type="info">{{ book.condition }}</el-tag>
              </div>
              <div class="book-footer">
                <span class="book-price">¥{{ book.price }}</span>
                <span class="book-seller">{{ book.seller }}</span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <el-empty v-if="books.length === 0 && !loading" description="暂无书籍" />
      
      <div class="pagination" v-if="total > 0">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="perPage"
          :total="total"
          layout="prev, pager, next"
          @current-change="handlePageChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getBooks } from '../api/book'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const books = ref([])
const page = ref(1)
const perPage = ref(20)
const total = ref(0)

const categoryName = computed(() => route.params.type)

const fetchBooks = async () => {
  loading.value = true
  try {
    const res = await getBooks({
      page: page.value,
      per_page: perPage.value,
      category: route.params.type
    })
    books.value = res.data.books
    total.value = res.data.total
  } finally {
    loading.value = false
  }
}

const handlePageChange = (newPage) => {
  page.value = newPage
  fetchBooks()
}

const goBack = () => {
  router.back()
}

const goToDetail = (id) => {
  router.push(`/book/${id}`)
}

onMounted(() => {
  fetchBooks()
})

watch(() => route.params.type, () => {
  page.value = 1
  fetchBooks()
})
</script>

<style scoped>
.category {
  max-width: 1400px;
  margin: 0 auto;
}

.book-list {
  margin-top: 20px;
  min-height: 400px;
}

.book-card {
  margin-bottom: 20px;
  cursor: pointer;
  transition: transform 0.3s;
}

.book-card:hover {
  transform: translateY(-5px);
}

.image-placeholder {
  width: 100%;
  height: 200px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f5f5;
}

.book-info {
  padding: 15px 0 0;
}

.book-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.book-author {
  color: #666;
  font-size: 14px;
  margin-bottom: 10px;
}

.book-meta {
  display: flex;
  gap: 8px;
  margin-bottom: 10px;
}

.book-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.book-price {
  color: #f56c6c;
  font-size: 18px;
  font-weight: bold;
}

.book-seller {
  color: #999;
  font-size: 12px;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 30px;
}
</style>
