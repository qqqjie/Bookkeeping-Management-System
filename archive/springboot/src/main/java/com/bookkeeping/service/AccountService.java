package com.bookkeeping.service;

import com.bookkeeping.dto.AccountSaveRequest;
import com.bookkeeping.vo.AccountVO;

import java.math.BigDecimal;
import java.util.List;

public interface AccountService {

    AccountVO create(Long userId, AccountSaveRequest request);

    AccountVO getById(Long userId, Long accountId);

    List<AccountVO> listByUserId(Long userId);

    AccountVO update(Long userId, Long accountId, AccountSaveRequest request);

    void delete(Long userId, Long accountId);

    BigDecimal getBalance(Long userId, Long accountId);
}
