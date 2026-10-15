package com.bookkeeping.service.impl;

import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import com.bookkeeping.dto.CategorySaveRequest;
import com.bookkeeping.entity.Category;
import com.bookkeeping.exception.BusinessException;
import com.bookkeeping.exception.ErrorCode;
import com.bookkeeping.mapper.CategoryMapper;
import com.bookkeeping.service.CategoryService;
import com.bookkeeping.vo.CategoryVO;
import lombok.RequiredArgsConstructor;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class CategoryServiceImpl implements CategoryService {

    private static final int STATUS_ACTIVE = 1;

    private final CategoryMapper categoryMapper;

    @Override
    @Transactional
    public CategoryVO create(Long userId, CategorySaveRequest request) {
        if (request.getParentId() != null) {
            validateParent(userId, request.getParentId(), request.getCategoryType());
        }
        if (existsByCategoryName(userId, request.getCategoryName(), request.getCategoryType(), null)) {
            throw new BusinessException(ErrorCode.CONFLICT, "同名同类型分类已存在");
        }
        Category category = new Category();
        category.setUserId(userId);
        category.setParentId(request.getParentId());
        category.setCategoryName(request.getCategoryName());
        category.setCategoryType(request.getCategoryType());
        category.setIcon(request.getIcon());
        category.setSortOrder(request.getSortOrder() != null ? request.getSortOrder() : 0);
        category.setStatus(STATUS_ACTIVE);
        categoryMapper.insert(category);
        return CategoryVO.from(category);
    }

    @Override
    public CategoryVO getById(Long userId, Long categoryId) {
        return CategoryVO.from(getOwnedCategory(userId, categoryId));
    }

    @Override
    public List<CategoryVO> listByUserId(Long userId) {
        List<Category> categories = categoryMapper.selectList(Wrappers.<Category>lambdaQuery()
                .and(wrapper -> wrapper.eq(Category::getUserId, userId)
                        .or()
                        .isNull(Category::getUserId))
                .eq(Category::getStatus, STATUS_ACTIVE)
                .orderByAsc(Category::getSortOrder)
                .orderByAsc(Category::getCategoryId));
        return categories.stream().map(CategoryVO::from).toList();
    }

    @Override
    @Transactional
    public CategoryVO update(Long userId, Long categoryId, CategorySaveRequest request) {
        Category category = getOwnedCategory(userId, categoryId);
        if (request.getParentId() != null) {
            if (request.getParentId().equals(categoryId)) {
                throw new BusinessException(ErrorCode.PARAM_INVALID, "父分类不能是自身");
            }
            validateParent(userId, request.getParentId(), request.getCategoryType());
        }
        if (!category.getCategoryName().equals(request.getCategoryName())
                && existsByCategoryName(userId, request.getCategoryName(), request.getCategoryType(), categoryId)) {
            throw new BusinessException(ErrorCode.CONFLICT, "同名同类型分类已存在");
        }
        category.setParentId(request.getParentId());
        category.setCategoryName(request.getCategoryName());
        category.setCategoryType(request.getCategoryType());
        category.setIcon(request.getIcon());
        if (request.getSortOrder() != null) {
            category.setSortOrder(request.getSortOrder());
        }
        categoryMapper.updateById(category);
        return CategoryVO.from(category);
    }

    @Override
    @Transactional
    public void delete(Long userId, Long categoryId) {
        getOwnedCategory(userId, categoryId);
        Long childCount = categoryMapper.selectCount(Wrappers.<Category>lambdaQuery()
                .eq(Category::getParentId, categoryId));
        if (childCount > 0) {
            throw new BusinessException(ErrorCode.CONFLICT, "该分类下存在子分类，无法删除");
        }
        try {
            categoryMapper.deleteById(categoryId);
        } catch (DataIntegrityViolationException ex) {
            throw new BusinessException(ErrorCode.CONFLICT, "该分类下存在交易流水，无法删除");
        }
    }

    private Category getOwnedCategory(Long userId, Long categoryId) {
        Category category = categoryMapper.selectById(categoryId);
        if (category == null || !userId.equals(category.getUserId())) {
            throw new BusinessException(ErrorCode.NOT_FOUND, "分类不存在");
        }
        return category;
    }

    private void validateParent(Long userId, Long parentId, com.bookkeeping.enums.CategoryType categoryType) {
        Category parent = categoryMapper.selectById(parentId);
        if (parent == null
                || (!userId.equals(parent.getUserId()) && parent.getUserId() != null)
                || !parent.getCategoryType().equals(categoryType)) {
            throw new BusinessException(ErrorCode.PARAM_INVALID, "父分类不存在、不属于当前用户或类型不一致");
        }
    }

    private boolean existsByCategoryName(Long userId, String categoryName,
                                         com.bookkeeping.enums.CategoryType categoryType,
                                         Long excludeCategoryId) {
        return categoryMapper.selectCount(Wrappers.<Category>lambdaQuery()
                .eq(Category::getUserId, userId)
                .eq(Category::getCategoryName, categoryName)
                .eq(Category::getCategoryType, categoryType)
                .ne(excludeCategoryId != null, Category::getCategoryId, excludeCategoryId)) > 0;
    }
}
