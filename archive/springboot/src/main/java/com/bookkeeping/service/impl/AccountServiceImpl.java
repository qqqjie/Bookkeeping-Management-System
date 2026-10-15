package com.bookkeeping.service.impl;

import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import com.bookkeeping.dto.AccountSaveRequest;
import com.bookkeeping.entity.Account;
import com.bookkeeping.exception.BusinessException;
import com.bookkeeping.exception.ErrorCode;
import com.bookkeeping.mapper.AccountMapper;
import com.bookkeeping.service.AccountService;
import com.bookkeeping.vo.AccountBalanceVO;
import com.bookkeeping.vo.AccountVO;
import lombok.RequiredArgsConstructor;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;

import java.math.BigDecimal;
import java.util.List;
import java.util.Map;
import java.util.function.Function;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class AccountServiceImpl implements AccountService {

    private static final int STATUS_ACTIVE = 1;

    private final AccountMapper accountMapper;

    @Override
    @Transactional
    public AccountVO create(Long userId, AccountSaveRequest request) {
        if (existsByAccountName(userId, request.getAccountName(), null)) {
            throw new BusinessException(ErrorCode.CONFLICT, "账户名称已存在");
        }
        Account account = new Account();
        account.setUserId(userId);
        account.setAccountName(request.getAccountName());
        account.setAccountType(request.getAccountType());
        account.setCurrency(StringUtils.hasText(request.getCurrency()) ? request.getCurrency() : "CNY");
        account.setInitialBalance(request.getInitialBalance() != null
                ? request.getInitialBalance() : BigDecimal.ZERO);
        account.setIncludeInTotal(request.getIncludeInTotal() != null
                ? request.getIncludeInTotal() : 1);
        account.setStatus(STATUS_ACTIVE);
        accountMapper.insert(account);
        return AccountVO.from(account);
    }

    @Override
    public AccountVO getById(Long userId, Long accountId) {
        return AccountVO.from(getOwnedAccount(userId, accountId));
    }

    @Override
    public List<AccountVO> listByUserId(Long userId) {
        List<Account> accounts = accountMapper.selectList(Wrappers.<Account>lambdaQuery()
                .eq(Account::getUserId, userId)
                .eq(Account::getStatus, STATUS_ACTIVE)
                .orderByDesc(Account::getCreatedAt));
        if (accounts.isEmpty()) {
            return List.of();
        }
        Map<Long, BigDecimal> balanceMap = getBalanceMap(userId);
        return accounts.stream()
                .map(account -> {
                    AccountVO vo = AccountVO.from(account);
                    vo.setCurrentBalance(balanceMap.getOrDefault(
                            account.getAccountId(), account.getInitialBalance()));
                    return vo;
                })
                .toList();
    }

    @Override
    @Transactional
    public AccountVO update(Long userId, Long accountId, AccountSaveRequest request) {
        Account account = getOwnedAccount(userId, accountId);
        if (!account.getAccountName().equals(request.getAccountName())
                && existsByAccountName(userId, request.getAccountName(), accountId)) {
            throw new BusinessException(ErrorCode.CONFLICT, "账户名称已存在");
        }
        account.setAccountName(request.getAccountName());
        account.setAccountType(request.getAccountType());
        account.setCurrency(StringUtils.hasText(request.getCurrency()) ? request.getCurrency() : "CNY");
        account.setInitialBalance(request.getInitialBalance() != null
                ? request.getInitialBalance() : BigDecimal.ZERO);
        account.setIncludeInTotal(request.getIncludeInTotal() != null
                ? request.getIncludeInTotal() : 1);
        accountMapper.updateById(account);
        return AccountVO.from(account);
    }

    @Override
    @Transactional
    public void delete(Long userId, Long accountId) {
        getOwnedAccount(userId, accountId);
        try {
            accountMapper.deleteById(accountId);
        } catch (DataIntegrityViolationException ex) {
            throw new BusinessException(ErrorCode.CONFLICT, "该账户下存在交易流水，无法删除");
        }
    }

    @Override
    public BigDecimal getBalance(Long userId, Long accountId) {
        getOwnedAccount(userId, accountId);
        return getBalanceMap(userId).getOrDefault(accountId, BigDecimal.ZERO);
    }

    private Account getOwnedAccount(Long userId, Long accountId) {
        Account account = accountMapper.selectById(accountId);
        if (account == null || !account.getUserId().equals(userId)) {
            throw new BusinessException(ErrorCode.NOT_FOUND, "账户不存在");
        }
        return account;
    }

    private boolean existsByAccountName(Long userId, String accountName, Long excludeAccountId) {
        return accountMapper.selectCount(Wrappers.<Account>lambdaQuery()
                .eq(Account::getUserId, userId)
                .eq(Account::getAccountName, accountName)
                .ne(excludeAccountId != null, Account::getAccountId, excludeAccountId)) > 0;
    }

    private Map<Long, BigDecimal> getBalanceMap(Long userId) {
        List<AccountBalanceVO> balances = accountMapper.selectBalancesByUserId(userId);
        return balances.stream().collect(Collectors.toMap(
                AccountBalanceVO::getAccountId,
                AccountBalanceVO::getCurrentBalance,
                (existing, replacement) -> existing));
    }
}
