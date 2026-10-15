<template>
  <div class="page-container">
    <div class="toolbar">
      <el-radio-group v-model="typeFilter" @change="onTypeFilterChange">
        <el-radio-button value="">全部</el-radio-button>
        <el-radio-button value="expense">支出分类</el-radio-button>
        <el-radio-button value="income">收入分类</el-radio-button>
      </el-radio-group>
      <div class="spacer" />
      <el-button type="primary" :icon="Plus" @click="openCreate">新增分类</el-button>
    </div>

    <el-card shadow="never">
      <el-table :data="filteredCategories" v-loading="loading" border stripe>
        <el-table-column prop="categoryName" label="名称" min-width="120" />
        <el-table-column label="类型" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.categoryType === 'income' ? 'danger' : 'success'" effect="light">
              {{ row.categoryType === 'income' ? '收入' : '支出' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="父分类" min-width="110">
          <template #default="{ row }">
            {{ row.parentId ? categoryName(row.parentId) : '—' }}
          </template>
        </el-table-column>
        <el-table-column prop="icon" label="图标" width="90" align="center">
          <template #default="{ row }">{{ row.icon || '—' }}</template>
        </el-table-column>
        <el-table-column prop="sortOrder" label="排序" width="80" align="center" />
        <el-table-column label="来源" width="110" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.userId === null" type="warning" effect="plain">系统预设</el-tag>
            <el-tag v-else type="info" effect="plain">自定义</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" align="center">
          <template #default="{ row }">
            <template v-if="row.userId === null">
              <el-tooltip content="系统预设分类不可修改" placement="top">
                <el-button link type="primary" disabled>编辑</el-button>
              </el-tooltip>
              <el-tooltip content="系统预设分类不可删除" placement="top">
                <el-button link type="danger" disabled>删除</el-button>
              </el-tooltip>
            </template>
            <template v-else>
              <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
              <el-button link type="danger" @click="onDelete(row)">删除</el-button>
            </template>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑分类' : '新增分类'" width="480px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="96px">
        <el-form-item label="分类名称" prop="categoryName">
          <el-input v-model="form.categoryName" maxlength="50" show-word-limit />
        </el-form-item>
        <el-form-item label="分类类型" prop="categoryType">
          <el-radio-group v-model="form.categoryType">
            <el-radio value="expense">支出</el-radio>
            <el-radio value="income">收入</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="父分类" prop="parentId">
          <el-select v-model="form.parentId" clearable placeholder="不选则为一级分类" style="width: 100%">
            <el-option
              v-for="item in parentOptions"
              :key="item.categoryId"
              :label="item.categoryName"
              :value="item.categoryId"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="图标标识" prop="icon">
          <el-input v-model="form.icon" maxlength="50" placeholder="选填，如 food" />
        </el-form-item>
        <el-form-item label="排序" prop="sortOrder">
          <el-input-number v-model="form.sortOrder" :min="0" :max="9999" />
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
import { categoriesApi } from '@/api/categories'

const loading = ref(false)
const dialogLoading = ref(false)
const dialogVisible = ref(false)
const editingId = ref(null)
const formRef = ref(null)
const categories = ref([])
const typeFilter = ref('')

const form = reactive({
  categoryName: '',
  categoryType: 'expense',
  parentId: null,
  icon: '',
  sortOrder: 0
})

const rules = {
  categoryName: [
    { required: true, message: '请输入分类名称', trigger: 'blur' },
    { max: 50, message: '分类名称长度不能超过 50', trigger: 'blur' }
  ],
  categoryType: [{ required: true, message: '请选择分类类型', trigger: 'change' }]
}

const filteredCategories = computed(() =>
  typeFilter.value
    ? categories.value.filter((item) => item.categoryType === typeFilter.value)
    : categories.value
)

const parentOptions = computed(() =>
  categories.value.filter(
    (item) =>
      item.categoryType === form.categoryType &&
      item.categoryId !== editingId.value &&
      !item.parentId
  )
)

function categoryName(id) {
  const found = categories.value.find((item) => item.categoryId === id)
  return found ? found.categoryName : `#${id}`
}

async function loadList() {
  loading.value = true
  try {
    categories.value = await categoriesApi.list()
  } finally {
    loading.value = false
  }
}

function onTypeFilterChange() {
  // 前端过滤，无需重新请求
}

function openCreate() {
  editingId.value = null
  Object.assign(form, {
    categoryName: '',
    categoryType: 'expense',
    parentId: null,
    icon: '',
    sortOrder: 0
  })
  dialogVisible.value = true
  formRef.value?.clearValidate()
}

function openEdit(row) {
  editingId.value = row.categoryId
  Object.assign(form, {
    categoryName: row.categoryName,
    categoryType: row.categoryType,
    parentId: row.parentId,
    icon: row.icon || '',
    sortOrder: row.sortOrder
  })
  dialogVisible.value = true
  formRef.value?.clearValidate()
}

async function onSubmit() {
  await formRef.value.validate()
  dialogLoading.value = true
  try {
    const payload = {
      categoryName: form.categoryName.trim(),
      categoryType: form.categoryType,
      parentId: form.parentId || undefined,
      icon: form.icon.trim() || undefined,
      sortOrder: form.sortOrder
    }
    if (editingId.value) {
      await categoriesApi.update(editingId.value, payload)
      ElMessage.success('已更新')
    } else {
      await categoriesApi.create(payload)
      ElMessage.success('已创建')
    }
    dialogVisible.value = false
    loadList()
  } finally {
    dialogLoading.value = false
  }
}

async function onDelete(row) {
  await ElMessageBox.confirm(`确认删除分类「${row.categoryName}」？`, '提示', { type: 'warning' })
  await categoriesApi.remove(row.categoryId)
  ElMessage.success('已删除')
  loadList()
}

onMounted(loadList)
</script>
