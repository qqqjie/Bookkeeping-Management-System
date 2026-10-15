export function formatMoney(value) {
  if (value === null || value === undefined || value === '') {
    return '0.00'
  }
  const num = Number(value)
  if (Number.isNaN(num)) {
    return String(value)
  }
  return num.toFixed(2)
}

export function formatMoneyWithSymbol(value) {
  return `¥${formatMoney(value)}`
}

export function formatPercent(value) {
  return `${formatMoney(value)}%`
}

export function formatDateTime(value) {
  if (!value) {
    return '-'
  }
  return String(value).replace('T', ' ').slice(0, 16)
}

export function formatMonth(value) {
  if (!value) {
    return '-'
  }
  return String(value).slice(0, 7)
}
