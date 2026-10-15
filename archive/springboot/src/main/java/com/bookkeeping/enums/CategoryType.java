package com.bookkeeping.enums;

import com.baomidou.mybatisplus.annotation.EnumValue;
import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonValue;

public enum CategoryType {

    INCOME("income"),
    EXPENSE("expense");

    @EnumValue
    private final String value;

    CategoryType(String value) {
        this.value = value;
    }

    @JsonValue
    public String getValue() {
        return value;
    }

    @JsonCreator
    public static CategoryType from(String value) {
        for (CategoryType categoryType : values()) {
            if (categoryType.value.equalsIgnoreCase(value)) {
                return categoryType;
            }
        }
        throw new IllegalArgumentException("未知的分类类型: " + value);
    }
}
