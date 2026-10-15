package com.bookkeeping.dto;

import com.bookkeeping.enums.CategoryType;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Data;

@Data
public class CategorySaveRequest {

    @NotBlank(message = "分类名称不能为空")
    @Size(max = 50, message = "分类名称长度不能超过 50")
    private String categoryName;

    @NotNull(message = "分类类型不能为空")
    private CategoryType categoryType;

    private Long parentId;

    @Size(max = 50, message = "图标标识长度不能超过 50")
    private String icon;

    private Integer sortOrder;
}
