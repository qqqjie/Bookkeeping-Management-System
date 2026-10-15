package com.bookkeeping.controller;

import com.bookkeeping.common.PageVO;
import com.bookkeeping.common.Result;
import com.bookkeeping.dto.TransactionQueryRequest;
import com.bookkeeping.dto.TransactionSaveRequest;
import com.bookkeeping.security.SecurityUtils;
import com.bookkeeping.service.TransactionService;
import com.bookkeeping.vo.TransactionVO;
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

@RestController
@RequestMapping("/api/v1/transactions")
@RequiredArgsConstructor
public class TransactionController {

    private final TransactionService transactionService;

    @PostMapping
    public Result<TransactionVO> create(@Valid @RequestBody TransactionSaveRequest request) {
        Long userId = SecurityUtils.getCurrentUserId();
        return Result.success(transactionService.create(userId, request));
    }

    @GetMapping
    public Result<PageVO<TransactionVO>> list(@Valid TransactionQueryRequest query) {
        Long userId = SecurityUtils.getCurrentUserId();
        return Result.success(transactionService.listByUserId(userId, query));
    }

    @GetMapping("/{transactionId}")
    public Result<TransactionVO> getById(@PathVariable Long transactionId) {
        Long userId = SecurityUtils.getCurrentUserId();
        return Result.success(transactionService.getById(userId, transactionId));
    }

    @PutMapping("/{transactionId}")
    public Result<TransactionVO> update(@PathVariable Long transactionId,
                                        @Valid @RequestBody TransactionSaveRequest request) {
        Long userId = SecurityUtils.getCurrentUserId();
        return Result.success(transactionService.update(userId, transactionId, request));
    }

    @DeleteMapping("/{transactionId}")
    public Result<Void> delete(@PathVariable Long transactionId) {
        Long userId = SecurityUtils.getCurrentUserId();
        transactionService.delete(userId, transactionId);
        return Result.success();
    }
}
