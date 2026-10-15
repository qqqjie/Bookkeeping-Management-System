package com.bookkeeping.vo;

import com.bookkeeping.entity.Category;
import com.bookkeeping.enums.CategoryType;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class CategoryVO {

    private Long categoryId;

    private Long userId;

    private Long parentId;

    private String categoryName;

    private CategoryType categoryType;

    private String icon;

    private Integer sortOrder;

    private Integer status;

    private LocalDateTime createdAt;

    public static CategoryVO from(Category category) {
        return new CategoryVO(
                category.getCategoryId(),
                category.getUserId(),
                category.getParentId(),
                category.getCategoryName(),
                category.getCategoryType(),
                category.getIcon(),
                category.getSortOrder(),
                category.getStatus(),
                category.getCreatedAt());
    }
}
