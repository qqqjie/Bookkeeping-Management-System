-- =====================================================================
-- 个人记账管理系统 · 数据库结构定义
-- 适用版本：MySQL 8.0（CHECK 约束自 8.0.16 起才被真正强制执行）
-- 存储引擎：InnoDB（MySQL 中支持外键约束的引擎）
-- 字符集  ：utf8mb4（每字符最多 4 字节，可存 Emoji 等补充平面字符）
-- 设计约定：
--   1. 所有金额字段使用 DECIMAL(15,2)，禁止使用 FLOAT/DOUBLE；
--   2. 交易金额恒为非负数，收入/支出方向由 transaction_type 决定；
--   3. 账户当前余额不落库冗余存储，由流水实时汇总计算；
--   4. 用户私有数据一律携带 user_id，便于按用户隔离与级联清理；
--   5. 停用一律走 status 字段，不做物理删除。
-- =====================================================================

CREATE DATABASE IF NOT EXISTS bookkeeping
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_0900_ai_ci;

USE bookkeeping;

-- ---------------------------------------------------------------------
-- 1. 用户表 users
-- ---------------------------------------------------------------------
CREATE TABLE users (
  user_id       BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '用户ID，主键',
  username      VARCHAR(50)  NOT NULL COMMENT '登录名，全局唯一',
  email         VARCHAR(100) NOT NULL COMMENT '邮箱，全局唯一',
  password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希值，禁止存明文',
  nickname      VARCHAR(50)  DEFAULT NULL COMMENT '昵称',
  status        TINYINT      NOT NULL DEFAULT 1 COMMENT '状态：1=正常，0=禁用',
  created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
  updated_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '资料更新时间',
  PRIMARY KEY (user_id),
  UNIQUE KEY uk_users_username (username),
  UNIQUE KEY uk_users_email (email)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci
  COMMENT = '用户表';

-- ---------------------------------------------------------------------
-- 2. 账户表 accounts（现金、借记卡、信用卡、支付宝、微信等）
-- ---------------------------------------------------------------------
CREATE TABLE accounts (
  account_id       BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '账户ID，主键',
  user_id          BIGINT UNSIGNED NOT NULL COMMENT '所属用户ID',
  account_name     VARCHAR(50) NOT NULL COMMENT '账户名称，如“招商银行信用卡”',
  account_type     ENUM('cash','debit_card','credit_card','alipay','wechat','other')
                   NOT NULL DEFAULT 'cash'
                   COMMENT '账户类型：现金/借记卡/信用卡/支付宝/微信/其他',
  currency         CHAR(3)      NOT NULL DEFAULT 'CNY' COMMENT '币种，ISO 4217 三位代码',
  initial_balance  DECIMAL(15,2) NOT NULL DEFAULT 0.00 COMMENT '开户初始余额',
  include_in_total TINYINT       NOT NULL DEFAULT 1 COMMENT '是否计入净资产统计：1=是，0=否（如信用卡负债可不计）',
  status           TINYINT       NOT NULL DEFAULT 1 COMMENT '状态：1=正常，0=停用',
  created_at       DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at       DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (account_id),
  -- 同一用户下账户名不可重复；该复合唯一索引的最左列为 user_id，
  -- 同时可服务“按用户列出全部账户”的查询，无需另建单列索引。
  UNIQUE KEY uk_accounts_user_name (user_id, account_name),
  CONSTRAINT fk_accounts_user
    FOREIGN KEY (user_id) REFERENCES users (user_id)
    ON DELETE CASCADE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci
  COMMENT = '账户表';

-- ---------------------------------------------------------------------
-- 3. 分类表 categories（餐饮/交通/工资等，支持二级分类）
--    user_id 为 NULL 表示系统预设分类，对所有用户可见；
--    parent_id 为 NULL 表示一级分类，自引用实现父子层级。
-- ---------------------------------------------------------------------
CREATE TABLE categories (
  category_id   BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '分类ID，主键',
  user_id       BIGINT UNSIGNED DEFAULT NULL COMMENT '所属用户ID；NULL=系统预设分类',
  parent_id     BIGINT UNSIGNED DEFAULT NULL COMMENT '父分类ID；NULL=一级分类',
  category_name VARCHAR(50)  NOT NULL COMMENT '分类名称',
  category_type ENUM('income','expense') NOT NULL COMMENT '分类类型：收入/支出',
  icon          VARCHAR(50)  DEFAULT NULL COMMENT '前端图标标识',
  sort_order    INT          NOT NULL DEFAULT 0 COMMENT '排序权重，数值越小越靠前',
  status        TINYINT      NOT NULL DEFAULT 1 COMMENT '状态：1=正常，0=停用',
  created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (category_id),
  UNIQUE KEY uk_categories_user_type_name (user_id, category_type, category_name),
  KEY idx_categories_parent (parent_id),
  CONSTRAINT fk_categories_user
    FOREIGN KEY (user_id) REFERENCES users (user_id)
    ON DELETE CASCADE,
  CONSTRAINT fk_categories_parent
    FOREIGN KEY (parent_id) REFERENCES categories (category_id)
    ON DELETE SET NULL
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci
  COMMENT = '分类表';

-- ---------------------------------------------------------------------
-- 4. 交易流水表 transactions（核心表，一笔收入或一条支出）
--    amount 恒为正数，方向由 transaction_type 决定；
--    transaction_time 记录业务发生时间，与 created_at（录入时间）分离。
-- ---------------------------------------------------------------------
CREATE TABLE transactions (
  transaction_id   BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '流水ID，主键',
  user_id          BIGINT UNSIGNED NOT NULL COMMENT '所属用户ID（冗余自账户，便于按用户聚合统计）',
  account_id       BIGINT UNSIGNED NOT NULL COMMENT '发生账户ID',
  category_id      BIGINT UNSIGNED NOT NULL COMMENT '所属分类ID',
  transaction_type ENUM('income','expense') NOT NULL COMMENT '流水类型：收入/支出',
  amount           DECIMAL(15,2) NOT NULL COMMENT '金额，恒为非负数，方向由类型决定',
  transaction_time DATETIME     NOT NULL COMMENT '交易发生时间',
  remark           VARCHAR(255) DEFAULT NULL COMMENT '备注',
  created_at       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
  updated_at       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '记录更新时间',
  PRIMARY KEY (transaction_id),
  -- 最高频查询：某用户的流水按时间倒序分页，DESC 索引免去额外排序
  KEY idx_transactions_user_time (user_id, transaction_time DESC),
  KEY idx_transactions_account (account_id),
  KEY idx_transactions_category (category_id),
  CONSTRAINT chk_transactions_amount CHECK (amount > 0),
  CONSTRAINT fk_transactions_user
    FOREIGN KEY (user_id) REFERENCES users (user_id)
    ON DELETE CASCADE,
  CONSTRAINT fk_transactions_account
    FOREIGN KEY (account_id) REFERENCES accounts (account_id)
    ON DELETE RESTRICT,
  CONSTRAINT fk_transactions_category
    FOREIGN KEY (category_id) REFERENCES categories (category_id)
    ON DELETE RESTRICT
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci
  COMMENT = '交易流水表';

-- ---------------------------------------------------------------------
-- 5. 系统预设分类种子数据（user_id = NULL，所有用户可见）
--    新库中 AUTO_INCREMENT 从 1 开始，首批 10 条依次占满 category_id 1-10。
-- ---------------------------------------------------------------------
INSERT INTO categories (user_id, parent_id, category_name, category_type, icon, sort_order) VALUES
(NULL, NULL, '餐饮',   'expense', 'food',      1),
(NULL, NULL, '交通',   'expense', 'transport', 2),
(NULL, NULL, '购物',   'expense', 'shopping',  3),
(NULL, NULL, '居住',   'expense', 'home',      4),
(NULL, NULL, '娱乐',   'expense', 'fun',       5),
(NULL, NULL, '医疗',   'expense', 'medical',   6),
(NULL, NULL, '工资',   'income',  'salary',    10),
(NULL, NULL, '奖金',   'income',  'bonus',     11),
(NULL, NULL, '理财收益', 'income', 'invest',   12),
(NULL, NULL, '兼职',   'income',  'parttime',  13);

-- 二级分类示例：演示 parent_id 用法（承接上批，餐饮的 category_id = 1）
INSERT INTO categories (user_id, parent_id, category_name, category_type, icon, sort_order) VALUES
(NULL, 1, '早餐', 'expense', 'breakfast', 1),
(NULL, 1, '午餐', 'expense', 'lunch',     2),
(NULL, 1, '晚餐', 'expense', 'dinner',    3);

-- ---------------------------------------------------------------------
-- 6. 常用查询示例：实时计算某用户各账户当前余额
--    余额 = initial_balance + 收入合计 - 支出合计
-- ---------------------------------------------------------------------
SELECT a.account_id,
       a.account_name,
       a.initial_balance
         + COALESCE(SUM(CASE WHEN t.transaction_type = 'income'  THEN t.amount END), 0)
         - COALESCE(SUM(CASE WHEN t.transaction_type = 'expense' THEN t.amount END), 0)
         AS current_balance
FROM accounts a
LEFT JOIN transactions t
       ON t.account_id = a.account_id
WHERE a.user_id = 1
GROUP BY a.account_id, a.account_name, a.initial_balance;
