<template>
  <div class="page-container">
    <div class="toolbar">
      <div class="spacer" />
      <el-button type="primary" :icon="Plus" @click="openCreate">新增账户</el-button>
    </div>

    <el-card shadow="never">
      <el-table :data="accounts" v-loading="loading" border stripe>
        <el-table-column prop="accountName" label="账户名称" min-width="140" />
        <el-table-column label="类型" width="110" align="center">
          <template #default="{ row }">
            <el-tag effect="plain">{{ typeLabel(row.accountType) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="currency" label="币种" width="80" align="center" />
        <el-table-column label="初始余额" width="140" align="right">
          <template #default="{ row }">
            <span class="money money-neutral">¥{{ formatMoney(row.initialBalance) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="实时余额" width="140" align="right">
          <template #default="{ row }">
            <span class="money money-income">¥{{ formatMoney(row.currentBalance) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="计入总资产" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="row.includeInTotal === 1 ? 'success' : 'info'" effect="light">
              {{ row.includeInTotal === 1 ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'" effect="light">
              {{ row.status === 1 ? '正常' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="130" align="center">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="onDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && accounts.length === 0" description="还没有账户，先创建一个吧" />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑账户' : '新增账户'" width="480px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="96px">
        <el-form-item label="账户名称" prop="accountName">
          <el-input v-model="form.accountName" maxlength="50" show-word-limit />
        </el-form-item>
        <el-form-item label="账户类型" prop="accountType">
          <el-select v-model="form.accountType" style="width: 100%">
            <el-option v-for="(label, value) in typeOptions" :key="value" :label="label" :value="value" />
          </el-select>
        </el-form-item>
        <el-form-item label="币种" prop="currency">
          <el-input v-model="form.currency" maxlength="3" placeholder="CNY" style="width: 120px" />
        </el-form-item>
        <el-form-item label="初始余额" prop="initialBalance">
          <el-input v-model="form.initialBalance" placeholder="如 1000.00" style="width: 200px">
            <template #prepend>¥</template>
          </el-input>
        </el-form-item>
        <el-form-item label="计入总资产" prop="includeInTotal">
          <el-switch v-model="form.includeInTotal" :active-value="1" :inactive-value="0" />
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
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { accountsApi } from '@/api/accounts'
import { formatMoney } from '@/utils/format'

const loading = ref(false)
const dialogLoading = ref(false)
const dialogVisible = ref(false)
const editingId = ref(null)
const formRef = ref(null)
const accounts = ref([])

const typeOptions = {
  cash: '现金',
  debit_card: '借记卡',
  credit_card: '信用卡',
  alipay: '支付宝',
  wechat: '微信',
  other: '其他'
}

const form = reactive({
  accountName: '',
  accountType: 'cash',
  currency: 'CNY',
  initialBalance: '0.00',
  includeInTotal: 1
})

const rules = {
  accountName: [
    { required: true, message: '请输入账户名称', trigger: 'blur' },
    { max: 50, message: '账户名称长度不能超过 50', trigger: 'blur' }
  ],
  accountType: [{ required: true, message: '请选择账户类型', trigger: 'change' }],
  currency: [
    { required: true, message: '请输入币种', trigger: 'blur' },
    { pattern: /^[A-Z]{3}$/, message: '币种须为三位大写字母，如 CNY', trigger: 'blur' }
  ],
  initialBalance: [
    { pattern: /^\d+(\.\d{1,2})?$/, message: '初始余额须为不小于 0 的数字，最多两位小数', trigger: 'blur' }
  ]
}

function typeLabel(value) {
  return typeOptions[value] || value
}

async function loadList() {
  loading.value = true
  try {
    accounts.value = await accountsApi.list()
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingId.value = null
  Object.assign(form, {
    accountName: '',
    accountType: 'cash',
    currency: 'CNY',
    initialBalance: '0.00',
    includeInTotal: 1
  })
  dialogVisible.value = true
  formRef.value?.clearValidate()
}

function openEdit(row) {
  editingId.value = row.accountId
  Object.assign(form, {
    accountName: row.accountName,
    accountType: row.accountType,
    currency: row.currency,
    initialBalance: row.initialBalance,
    includeInTotal: row.includeInTotal
  })
  dialogVisible.value = true
  formRef.value?.clearValidate()
}

async function onSubmit() {
  await formRef.value.validate()
  dialogLoading.value = true
  try {
    const payload = {
      accountName: form.accountName.trim(),
      accountType: form.accountType,
      currency: form.currency.trim().toUpperCase(),
      initialBalance: form.initialBalance || '0.00',
      includeInTotal: form.includeInTotal
    }
    if (editingId.value) {
      await accountsApi.update(editingId.value, payload)
      ElMessage.success('已更新')
    } else {
      await accountsApi.create(payload)
      ElMessage.success('已创建')
    }
    dialogVisible.value = false
    loadList()
  } finally {
    dialogLoading.value = false
  }
}

async function onDelete(row) {
  await ElMessageBox.confirm(`确认删除账户「${row.accountName}」？`, '提示', { type: 'warning' })
  await accountsApi.remove(row.accountId)
  ElMessage.success('已删除')
  loadList()
}

onMounted(loadList)
</script>
