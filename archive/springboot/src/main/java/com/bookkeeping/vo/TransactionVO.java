package com.bookkeeping.vo;

import com.bookkeeping.entity.Transaction;
import com.bookkeeping.enums.TransactionType;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class TransactionVO {

    private Long transactionId;

    private Long accountId;

    private Long categoryId;

    private TransactionType transactionType;

    private BigDecimal amount;

    private LocalDateTime transactionTime;

    private String remark;

    private LocalDateTime createdAt;

    public static TransactionVO from(Transaction transaction) {
        return new TransactionVO(
                transaction.getTransactionId(),
                transaction.getAccountId(),
                transaction.getCategoryId(),
                transaction.getTransactionType(),
                transaction.getAmount(),
                transaction.getTransactionTime(),
                transaction.getRemark(),
                transaction.getCreatedAt());
    }
}
