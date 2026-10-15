package com.bookkeeping.enums;

import com.baomidou.mybatisplus.annotation.EnumValue;
import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonValue;

public enum AccountType {

    CASH("cash"),
    DEBIT_CARD("debit_card"),
    CREDIT_CARD("credit_card"),
    ALIPAY("alipay"),
    WECHAT("wechat"),
    OTHER("other");

    @EnumValue
    private final String value;

    AccountType(String value) {
        this.value = value;
    }

    @JsonValue
    public String getValue() {
        return value;
    }

    @JsonCreator
    public static AccountType from(String value) {
        for (AccountType accountType : values()) {
            if (accountType.value.equalsIgnoreCase(value)) {
                return accountType;
            }
        }
        throw new IllegalArgumentException("未知的账户类型: " + value);
    }
}
