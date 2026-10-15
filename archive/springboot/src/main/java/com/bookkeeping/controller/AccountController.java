package com.bookkeeping.controller;

import com.bookkeeping.common.Result;
import com.bookkeeping.dto.AccountSaveRequest;
import com.bookkeeping.security.SecurityUtils;
import com.bookkeeping.service.AccountService;
import com.bookkeeping.vo.AccountVO;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.math.BigDecimal;
import java.util.List;

@RestController
@RequestMapping("/api/v1/accounts")
@RequiredArgsConstructor
public class AccountController {

    private final AccountService accountService;

    @PostMapping
    public Result<AccountVO> create(@Valid @RequestBody AccountSaveRequest request) {
        Long userId = SecurityUtils.getCurrentUserId();
        return Result.success(accountService.create(userId, request));
    }

    @GetMapping
    public Result<List<AccountVO>> list() {
        Long userId = SecurityUtils.getCurrentUserId();
        return Result.success(accountService.listByUserId(userId));
    }

    @GetMapping("/{accountId}")
    public Result<AccountVO> getById(@PathVariable Long accountId) {
        Long userId = SecurityUtils.getCurrentUserId();
        return Result.success(accountService.getById(userId, accountId));
    }

    @GetMapping("/{accountId}/balance")
    public Result<BigDecimal> getBalance(@PathVariable Long accountId) {
        Long userId = SecurityUtils.getCurrentUserId();
        return Result.success(accountService.getBalance(userId, accountId));
    }

    @PutMapping("/{accountId}")
    public Result<AccountVO> update(@PathVariable Long accountId,
                                    @Valid @RequestBody AccountSaveRequest request) {
        Long userId = SecurityUtils.getCurrentUserId();
        return Result.success(accountService.update(userId, accountId, request));
    }

    @DeleteMapping("/{accountId}")
    public Result<Void> delete(@PathVariable Long accountId) {
        Long userId = SecurityUtils.getCurrentUserId();
        accountService.delete(userId, accountId);
        return Result.success();
    }
}
