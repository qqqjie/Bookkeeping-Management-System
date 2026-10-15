package com.bookkeeping.service;

import com.bookkeeping.dto.CategorySaveRequest;
import com.bookkeeping.vo.CategoryVO;

import java.util.List;

public interface CategoryService {

    CategoryVO create(Long userId, CategorySaveRequest request);

    CategoryVO getById(Long userId, Long categoryId);

    List<CategoryVO> listByUserId(Long userId);

    CategoryVO update(Long userId, Long categoryId, CategorySaveRequest request);

    void delete(Long userId, Long categoryId);
}
