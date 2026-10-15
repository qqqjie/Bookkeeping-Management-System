import request from './request'

export const statsApi = {
  monthlySummary: (month) => request.get('/stats/monthly-summary', { params: { month } }),
  categoryShare: (month, type) =>
    request.get('/stats/category-share', { params: { month, transactionType: type } }),
  trend: (months) => request.get('/stats/trend', { params: { months } })
}
