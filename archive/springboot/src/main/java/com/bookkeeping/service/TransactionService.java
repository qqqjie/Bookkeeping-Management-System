package com.bookkeeping.service;

import com.bookkeeping.common.PageVO;
import com.bookkeeping.dto.TransactionQueryRequest;
import com.bookkeeping.dto.TransactionSaveRequest;
import com.bookkeeping.vo.TransactionVO;

public interface TransactionService {

    TransactionVO create(Long userId, TransactionSaveRequest request);

    TransactionVO getById(Long userId, Long transactionId);

    PageVO<TransactionVO> listByUserId(Long userId, TransactionQueryRequest query);

    TransactionVO update(Long userId, Long transactionId, TransactionSaveRequest request);

    void delete(Long userId, Long transactionId);
}
