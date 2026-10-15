package com.bookkeeping.controller;

import com.bookkeeping.common.Result;
import com.bookkeeping.dto.CategorySaveRequest;
import com.bookkeeping.security.SecurityUtils;
import com.bookkeeping.service.CategoryService;
import com.bookkeeping.vo.CategoryVO;
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

import java.util.List;

@RestController
@RequestMapping("/api/v1/categories")
@RequiredArgsConstructor
public class CategoryController {

    private final CategoryService categoryService;

    @PostMapping
    public Result<CategoryVO> create(@Valid @RequestBody CategorySaveRequest request) {
        Long userId = SecurityUtils.getCurrentUserId();
        return Result.success(categoryService.create(userId, request));
    }

    @GetMapping
    public Result<List<CategoryVO>> list() {
        Long userId = SecurityUtils.getCurrentUserId();
        return Result.success(categoryService.listByUserId(userId));
    }

    @GetMapping("/{categoryId}")
    public Result<CategoryVO> getById(@PathVariable Long categoryId) {
        Long userId = SecurityUtils.getCurrentUserId();
        return Result.success(categoryService.getById(userId, categoryId));
    }

    @PutMapping("/{categoryId}")
    public Result<CategoryVO> update(@PathVariable Long categoryId,
                                     @Valid @RequestBody CategorySaveRequest request) {
        Long userId = SecurityUtils.getCurrentUserId();
        return Result.success(categoryService.update(userId, categoryId, request));
    }

    @DeleteMapping("/{categoryId}")
    public Result<Void> delete(@PathVariable Long categoryId) {
        Long userId = SecurityUtils.getCurrentUserId();
        categoryService.delete(userId, categoryId);
        return Result.success();
    }
}
