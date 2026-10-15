-- bookkeeping_app 专用账户：仅对 bookkeeping 库有权限
-- 执行前将下方密码占位符替换为真实密码（或改用 mysql Config 文件注入）
CREATE USER IF NOT EXISTS 'bookkeeping_app'@'%' IDENTIFIED BY 'CHANGE_ME_APP_PASSWORD';
GRANT ALL PRIVILEGES ON bookkeeping.* TO 'bookkeeping_app'@'%';
FLUSH PRIVILEGES;
