<template>
  <div class="page-container">
    <el-row :gutter="16">
      <el-col :span="8">
        <el-card shadow="never">
          <div class="stat-label">本月收入</div>
          <div class="stat-value money-income">+{{ formatMoney(summary?.totalIncome) }}</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never">
          <div class="stat-label">本月支出</div>
          <div class="stat-value money-expense">-{{ formatMoney(summary?.totalExpense) }}</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never">
          <div class="stat-label">本月结余</div>
          <div :class="['stat-value', netAmount >= 0 ? 'money-income' : 'money-expense']">
            {{ netAmount >= 0 ? '+' : '' }}{{ formatMoney(summary?.netAmount) }}
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :span="10">
        <el-card shadow="never">
          <div class="card-title">本月支出分类占比</div>
          <div ref="pieRef" class="chart"></div>
          <el-empty v-if="!loading && share.length === 0" description="本月暂无支出记录" />
        </el-card>
      </el-col>
      <el-col :span="14">
        <el-card shadow="never">
          <div class="card-title">近 6 个月收支趋势</div>
          <div ref="lineRef" class="chart"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import * as echarts from 'echarts'
import { statsApi } from '@/api/stats'
import { formatMoney } from '@/utils/format'

const loading = ref(false)
const summary = ref(null)
const share = ref([])
const trend = ref([])
const pieRef = ref(null)
const lineRef = ref(null)
let pieInstance = null
let lineInstance = null

const netAmount = computed(() => Number(summary.value?.netAmount ?? 0))

function currentMonth() {
  const now = new Date()
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
}

async function loadData() {
  loading.value = true
  try {
    const month = currentMonth()
    const [summaryData, shareData, trendData] = await Promise.all([
      statsApi.monthlySummary(month),
      statsApi.categoryShare(month, 'expense'),
      statsApi.trend(6)
    ])
    summary.value = summaryData
    share.value = shareData
    trend.value = trendData
    renderPie()
    renderLine()
  } finally {
    loading.value = false
  }
}

function renderPie() {
  if (!pieInstance) {
    return
  }
  pieInstance.setOption(
    {
      tooltip: {
        trigger: 'item',
        formatter: (item) =>
          `${item.name}<br/>金额：¥${formatMoney(item.value)}（${item.percent}%）`
      },
      legend: { bottom: 0, type: 'scroll' },
      series: [
        {
          type: 'pie',
          radius: ['40%', '68%'],
          itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
          label: { formatter: '{b}\n{d}%' },
          data: share.value.map((item) => ({
            name: item.categoryName,
            value: Number(item.amount)
          }))
        }
      ]
    },
    true
  )
}

function renderLine() {
  if (!lineInstance) {
    return
  }
  lineInstance.setOption(
    {
      tooltip: {
        trigger: 'axis',
        valueFormatter: (value) => `¥${formatMoney(value)}`
      },
      legend: { data: ['收入', '支出'] },
      grid: { left: 56, right: 24, top: 40, bottom: 32 },
      xAxis: { type: 'category', data: trend.value.map((item) => item.month) },
      yAxis: { type: 'value' },
      series: [
        {
          name: '收入',
          type: 'line',
          smooth: true,
          data: trend.value.map((item) => Number(item.totalIncome)),
          itemStyle: { color: '#f56c6c' },
          areaStyle: { opacity: 0.08 }
        },
        {
          name: '支出',
          type: 'line',
          smooth: true,
          data: trend.value.map((item) => Number(item.totalExpense)),
          itemStyle: { color: '#67c23a' },
          areaStyle: { opacity: 0.08 }
        }
      ]
    },
    true
  )
}

function onResize() {
  pieInstance?.resize()
  lineInstance?.resize()
}

onMounted(async () => {
  pieInstance = echarts.init(pieRef.value)
  lineInstance = echarts.init(lineRef.value)
  window.addEventListener('resize', onResize)
  await loadData()
})

onUnmounted(() => {
  window.removeEventListener('resize', onResize)
  pieInstance?.dispose()
  lineInstance?.dispose()
})
</script>

<style scoped>
.stat-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 26px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}
</style>
