package com.bookkeeping.service.impl;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bookkeeping.common.PageVO;
import com.bookkeeping.dto.TransactionQueryRequest;
import com.bookkeeping.dto.TransactionSaveRequest;
import com.bookkeeping.entity.Account;
import com.bookkeeping.entity.Category;
import com.bookkeeping.entity.Transaction;
import com.bookkeeping.exception.BusinessException;
import com.bookkeeping.exception.ErrorCode;
import com.bookkeeping.mapper.AccountMapper;
import com.bookkeeping.mapper.CategoryMapper;
import com.bookkeeping.mapper.TransactionMapper;
import com.bookkeeping.service.TransactionService;
import com.bookkeeping.vo.TransactionVO;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class TransactionServiceImpl implements TransactionService {

    private final TransactionMapper transactionMapper;

    private final AccountMapper accountMapper;

    private final CategoryMapper categoryMapper;

    @Override
    @Transactional
    public TransactionVO create(Long userId, TransactionSaveRequest request) {
        validateReferences(userId, request);
        Transaction transaction = new Transaction();
        transaction.setUserId(userId);
        transaction.setAccountId(request.getAccountId());
        transaction.setCategoryId(request.getCategoryId());
        transaction.setTransactionType(request.getTransactionType());
        transaction.setAmount(request.getAmount());
        transaction.setTransactionTime(request.getTransactionTime());
        transaction.setRemark(request.getRemark());
        transactionMapper.insert(transaction);
        return TransactionVO.from(transaction);
    }

    @Override
    public TransactionVO getById(Long userId, Long transactionId) {
        return TransactionVO.from(getOwnedTransaction(userId, transactionId));
    }

    @Override
    public PageVO<TransactionVO> listByUserId(Long userId, TransactionQueryRequest query) {
        Page<Transaction> page = new Page<>(query.getPage(), query.getSize());
        IPage<Transaction> resultPage = transactionMapper.selectPage(page, Wrappers.<Transaction>lambdaQuery()
                .eq(Transaction::getUserId, userId)
                .eq(query.getAccountId() != null, Transaction::getAccountId, query.getAccountId())
                .eq(query.getCategoryId() != null, Transaction::getCategoryId, query.getCategoryId())
                .eq(query.getTransactionType() != null, Transaction::getTransactionType, query.getTransactionType())
                .ge(query.getStartTime() != null, Transaction::getTransactionTime, query.getStartTime())
                .le(query.getEndTime() != null, Transaction::getTransactionTime, query.getEndTime())
                .orderByDesc(Transaction::getTransactionTime));
        return PageVO.from(resultPage, TransactionVO::from);
    }

    @Override
    @Transactional
    public TransactionVO update(Long userId, Long transactionId, TransactionSaveRequest request) {
        Transaction transaction = getOwnedTransaction(userId, transactionId);
        validateReferences(userId, request);
        transaction.setAccountId(request.getAccountId());
        transaction.setCategoryId(request.getCategoryId());
        transaction.setTransactionType(request.getTransactionType());
        transaction.setAmount(request.getAmount());
        transaction.setTransactionTime(request.getTransactionTime());
        transaction.setRemark(request.getRemark());
        transactionMapper.updateById(transaction);
        return TransactionVO.from(transaction);
    }

    @Override
    @Transactional
    public void delete(Long userId, Long transactionId) {
        getOwnedTransaction(userId, transactionId);
        transactionMapper.deleteById(transactionId);
    }

    private Transaction getOwnedTransaction(Long userId, Long transactionId) {
        Transaction transaction = transactionMapper.selectById(transactionId);
        if (transaction == null || !transaction.getUserId().equals(userId)) {
            throw new BusinessException(ErrorCode.NOT_FOUND, "交易流水不存在");
        }
        return transaction;
    }

    private void validateReferences(Long userId, TransactionSaveRequest request) {
        Account account = accountMapper.selectById(request.getAccountId());
        if (account == null || !account.getUserId().equals(userId)) {
            throw new BusinessException(ErrorCode.NOT_FOUND, "账户不存在");
        }
        Category category = categoryMapper.selectById(request.getCategoryId());
        if (category == null
                || (!userId.equals(category.getUserId()) && category.getUserId() != null)) {
            throw new BusinessException(ErrorCode.NOT_FOUND, "分类不存在");
        }
    }
}
