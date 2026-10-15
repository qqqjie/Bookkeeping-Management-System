package com.bookkeeping.vo;

import com.bookkeeping.entity.Account;
import com.bookkeeping.enums.AccountType;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class AccountVO {

    private Long accountId;

    private String accountName;

    private AccountType accountType;

    private String currency;

    private BigDecimal initialBalance;

    private Integer includeInTotal;

    private Integer status;

    private LocalDateTime createdAt;

    private BigDecimal currentBalance;

    public static AccountVO from(Account account) {
        return new AccountVO(
                account.getAccountId(),
                account.getAccountName(),
                account.getAccountType(),
                account.getCurrency(),
                account.getInitialBalance(),
                account.getIncludeInTotal(),
                account.getStatus(),
                account.getCreatedAt(),
                null);
    }
}
