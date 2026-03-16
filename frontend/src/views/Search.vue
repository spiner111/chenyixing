<template>
  <div class="search">
    <!-- 搜索栏 -->
    <div class="search-bar">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索书名"
        size="large"
        clearable
        @keyup.enter="handleSearch"
      >
        <template #append>
          <el-button @click="handleSearch">
            <el-icon><Search /></el-icon>
          </el-button>
        </template>
      </el-input>
    </div>

    <!-- 筛选条件 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="分类">
          <el-select v-model="filterForm.category" placeholder="全部" clearable size="large">
            <el-option label="教材类" value="教材类" />
            <el-option label="考研资料" value="考研资料" />
            <el-option label="课外阅读" value="课外阅读" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="成色">
          <el-select v-model="filterForm.condition" placeholder="全部" clearable size="large">
            <el-option label="全新" value="全新" />
            <el-option label="九成新" value="九成新" />
            <el-option label="八成新" value="八成新" />
            <el-option label="七成新" value="七成新" />
            <el-option label="及以下" value="及以下" />
          </el-select>
        </el-form-item>
        <el-form-item label="价格">
          <el-input-number
            v-model="filterForm.min_price"
            :min="0"
            size="large"
            placeholder="最低"
            style="width: 120px"
          />
          <span style="margin: 0 8px">-</span>
          <el-input-number
            v-model="filterForm.max_price"
            :min="0"
            size="large"
            placeholder="最高"
            style="width: 120px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" @click="handleSearch">搜索</el-button>
          <el-button size="large" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 书籍列表 -->
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

      <el-empty v-if="books.length === 0 && !loading" description="暂无搜索结果" />

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
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { searchBooks } from '../api/book'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const books = ref([])
const page = ref(1)
const perPage = ref(20)
const total = ref(0)
const searchKeyword = ref('')

const filterForm = reactive({
  category: '',
  condition: '',
  min_price: undefined,
  max_price: undefined
})

const fetchBooks = async () => {
  loading.value = true
  try {
    const params = {
      keyword: searchKeyword.value,
      page: page.value,
      per_page: perPage.value,
      ...filterForm
    }
    if (params.min_price === undefined) delete params.min_price
    if (params.max_price === undefined) delete params.max_price
    
    const res = await searchBooks(params)
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

const handleSearch = () => {
  page.value = 1
  fetchBooks()
}

const handleReset = () => {
  searchKeyword.value = ''
  filterForm.category = ''
  filterForm.condition = ''
  filterForm.min_price = undefined
  filterForm.max_price = undefined
  page.value = 1
  fetchBooks()
}

const goToDetail = (id) => {
  router.push(`/book/${id}`)
}

onMounted(() => {
  if (route.query.keyword) {
    searchKeyword.value = route.query.keyword
  }
  fetchBooks()
})
</script>

<style scoped>
.search {
  max-width: 1400px;
  margin: 0 auto;
}

.search-bar {
  max-width: 600px;
  margin: 0 auto 20px;
}

.filter-card {
  margin-bottom: 20px;
}

.book-list {
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
