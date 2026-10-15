package com.bookkeeping.enums;

import com.baomidou.mybatisplus.annotation.EnumValue;
import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonValue;

public enum TransactionType {

    INCOME("income"),
    EXPENSE("expense");

    @EnumValue
    private final String value;

    TransactionType(String value) {
        this.value = value;
    }

    @JsonValue
    public String getValue() {
        return value;
    }

    @JsonCreator
    public static TransactionType from(String value) {
        for (TransactionType transactionType : values()) {
            if (transactionType.value.equalsIgnoreCase(value)) {
                return transactionType;
            }
        }
        throw new IllegalArgumentException("未知的交易类型: " + value);
    }
}
