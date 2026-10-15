package com.bookkeeping.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.bookkeeping.entity.Account;
import com.bookkeeping.vo.AccountBalanceVO;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.util.List;

@Mapper
public interface AccountMapper extends BaseMapper<Account> {

    @Select("SELECT a.account_id AS accountId, "
            + "a.initial_balance + COALESCE(SUM(CASE WHEN t.transaction_type = 'income' THEN t.amount END), 0) "
            + "- COALESCE(SUM(CASE WHEN t.transaction_type = 'expense' THEN t.amount END), 0) AS currentBalance "
            + "FROM accounts a LEFT JOIN transactions t ON t.account_id = a.account_id "
            + "WHERE a.user_id = #{userId} "
            + "GROUP BY a.account_id, a.initial_balance")
    List<AccountBalanceVO> selectBalancesByUserId(@Param("userId") Long userId);
}
