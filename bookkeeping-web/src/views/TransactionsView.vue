<template>
  <div class="page-container">
    <div class="toolbar">
      <el-date-picker
        v-model="query.month"
        type="month"
        value-format="YYYY-MM"
        placeholder="月份"
        clearable
        style="width: 140px"
      />
      <el-select v-model="query.transactionType" placeholder="类型" clearable style="width: 110px">
        <el-option label="收入" value="income" />
        <el-option label="支出" value="expense" />
      </el-select>
      <el-select v-model="query.accountId" placeholder="账户" clearable style="width: 150px">
        <el-option v-for="item in accounts" :key="item.accountId" :label="item.accountName" :value="item.accountId" />
      </el-select>
      <el-select v-model="query.categoryId" placeholder="分类" clearable style="width: 150px">
        <el-option v-for="item in categories" :key="item.categoryId" :label="item.categoryName" :value="item.categoryId" />
      </el-select>
      <el-button type="primary" @click="onSearch">查询</el-button>
      <el-button @click="onReset">重置</el-button>
      <div class="spacer" />
      <el-button type="primary" :icon="Plus" @click="openCreate">记一笔</el-button>
    </div>

    <el-card shadow="never">
      <el-table :data="tableData" v-loading="loading" border stripe>
        <el-table-column prop="transactionTime" label="交易时间" width="170">
          <template #default="{ row }">{{ formatDateTime(row.transactionTime) }}</template>
        </el-table-column>
        <el-table-column label="类型" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.transactionType === 'income' ? 'danger' : 'success'" effect="light">
              {{ row.transactionType === 'income' ? '收入' : '支出' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="账户" min-width="120">
          <template #default="{ row }">{{ accountName(row.accountId) }}</template>
        </el-table-column>
        <el-table-column label="分类" min-width="110">
          <template #default="{ row }">{{ categoryName(row.categoryId) }}</template>
        </el-table-column>
        <el-table-column label="金额" width="140" align="right">
          <template #default="{ row }">
            <span :class="['money', row.transactionType === 'income' ? 'money-income' : 'money-expense']">
              {{ row.transactionType === 'income' ? '+' : '-' }}{{ formatMoney(row.amount) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="140" show-overflow-tooltip />
        <el-table-column label="操作" width="130" align="center">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="onDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          background
          layout="total, sizes, prev, pager, next"
          :total="total"
          :current-page="query.page"
          :page-size="query.size"
          :page-sizes="[10, 20, 50, 100]"
          @current-change="onPageChange"
          @size-change="onSizeChange"
        />
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑流水' : '记一笔'" width="480px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="类型" prop="transactionType">
          <el-radio-group v-model="form.transactionType">
            <el-radio value="expense">支出</el-radio>
            <el-radio value="income">收入</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="账户" prop="accountId">
          <el-select v-model="form.accountId" placeholder="请选择账户" style="width: 100%">
            <el-option v-for="item in accounts" :key="item.accountId" :label="item.accountName" :value="item.accountId" />
          </el-select>
        </el-form-item>
        <el-form-item label="分类" prop="categoryId">
          <el-select v-model="form.categoryId" placeholder="请选择分类" style="width: 100%">
            <el-option
              v-for="item in filteredCategories"
              :key="item.categoryId"
              :label="item.categoryName"
              :value="item.categoryId"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="金额" prop="amount">
          <el-input v-model="form.amount" placeholder="如 35.50" style="width: 100%">
            <template #prepend>¥</template>
          </el-input>
        </el-form-item>
        <el-form-item label="交易时间" prop="transactionTime">
          <el-date-picker
            v-model="form.transactionTime"
            type="datetime"
            value-format="YYYY-MM-DDTHH:mm:ss"
            placeholder="选择交易时间"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="form.remark" type="textarea" :rows="2" maxlength="255" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="dialogLoading" @click="onSubmit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { accountsApi } from '@/api/accounts'
import { categoriesApi } from '@/api/categories'
import { transactionsApi } from '@/api/transactions'
import { formatDateTime, formatMoney } from '@/utils/format'

const loading = ref(false)
const dialogLoading = ref(false)
const dialogVisible = ref(false)
const editingId = ref(null)
const formRef = ref(null)

const query = reactive({
  month: '',
  transactionType: '',
  accountId: '',
  categoryId: '',
  page: 1,
  size: 20
})
const tableData = ref([])
const total = ref(0)
const accounts = ref([])
const categories = ref([])

const form = reactive({
  accountId: null,
  categoryId: null,
  transactionType: 'expense',
  amount: '',
  transactionTime: '',
  remark: ''
})

const rules = {
  accountId: [{ required: true, message: '请选择账户', trigger: 'change' }],
  categoryId: [{ required: true, message: '请选择分类', trigger: 'change' }],
  transactionType: [{ required: true, message: '请选择类型', trigger: 'change' }],
  amount: [
    { required: true, message: '请输入金额', trigger: 'blur' },
    { pattern: /^\d+(\.\d{1,2})?$/, message: '金额须为不小于 0 的数字，最多两位小数', trigger: 'blur' }
  ],
  transactionTime: [{ required: true, message: '请选择交易时间', trigger: 'change' }]
}

const filteredCategories = computed(() =>
  categories.value.filter((item) => item.categoryType === form.transactionType)
)

function accountName(id) {
  const found = accounts.value.find((item) => item.accountId === id)
  return found ? found.accountName : `#${id}`
}

function categoryName(id) {
  const found = categories.value.find((item) => item.categoryId === id)
  return found ? found.categoryName : `#${id}`
}

async function loadBaseData() {
  const [accountList, categoryList] = await Promise.all([
    accountsApi.list(),
    categoriesApi.list()
  ])
  accounts.value = accountList
  categories.value = categoryList
}

async function loadList() {
  loading.value = true
  try {
    const params = { page: query.page, size: query.size }
    if (query.month) params.month = query.month
    if (query.transactionType) params.transactionType = query.transactionType
    if (query.accountId) params.accountId = query.accountId
    if (query.categoryId) params.categoryId = query.categoryId
    const data = await transactionsApi.list(params)
    tableData.value = data.records
    total.value = data.total
  } finally {
    loading.value = false
  }
}

function onSearch() {
  query.page = 1
  loadList()
}

function onReset() {
  Object.assign(query, {
    month: '',
    transactionType: '',
    accountId: '',
    categoryId: '',
    page: 1,
    size: 20
  })
  loadList()
}

function onPageChange(page) {
  query.page = page
  loadList()
}

function onSizeChange(size) {
  query.size = size
  query.page = 1
  loadList()
}

function defaultTime() {
  const now = new Date()
  const pad = (value) => String(value).padStart(2, '0')
  return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}T${pad(
    now.getHours()
  )}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`
}

function openCreate() {
  editingId.value = null
  Object.assign(form, {
    accountId: accounts.value[0]?.accountId ?? null,
    categoryId: null,
    transactionType: 'expense',
    amount: '',
    transactionTime: defaultTime(),
    remark: ''
  })
  dialogVisible.value = true
  formRef.value?.clearValidate()
}

function openEdit(row) {
  editingId.value = row.transactionId
  Object.assign(form, {
    accountId: row.accountId,
    categoryId: row.categoryId,
    transactionType: row.transactionType,
    amount: row.amount,
    transactionTime: row.transactionTime,
    remark: row.remark || ''
  })
  dialogVisible.value = true
  formRef.value?.clearValidate()
}

async function onSubmit() {
  await formRef.value.validate()
  dialogLoading.value = true
  try {
    const payload = {
      accountId: form.accountId,
      categoryId: form.categoryId,
      transactionType: form.transactionType,
      amount: form.amount,
      transactionTime: form.transactionTime,
      remark: form.remark || undefined
    }
    if (editingId.value) {
      await transactionsApi.update(editingId.value, payload)
      ElMessage.success('已更新')
    } else {
      await transactionsApi.create(payload)
      ElMessage.success('已记账')
    }
    dialogVisible.value = false
    loadList()
  } finally {
    dialogLoading.value = false
  }
}

async function onDelete(row) {
  await ElMessageBox.confirm(
    `确认删除该笔${row.transactionType === 'income' ? '收入' : '支出'}记录？`,
    '提示',
    { type: 'warning' }
  )
  await transactionsApi.remove(row.transactionId)
  ElMessage.success('已删除')
  if (tableData.value.length === 1 && query.page > 1) {
    query.page -= 1
  }
  loadList()
}

onMounted(async () => {
  await loadBaseData()
  await loadList()
})
</script>

<style scoped>
.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
