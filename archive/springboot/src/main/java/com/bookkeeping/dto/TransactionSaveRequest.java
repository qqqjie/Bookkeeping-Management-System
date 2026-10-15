package com.bookkeeping.dto;

import com.bookkeeping.enums.TransactionType;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
public class TransactionSaveRequest {

    @NotNull(message = "账户ID不能为空")
    private Long accountId;

    @NotNull(message = "分类ID不能为空")
    private Long categoryId;

    @NotNull(message = "交易类型不能为空")
    private TransactionType transactionType;

    @NotNull(message = "金额不能为空")
    @DecimalMin(value = "0.01", message = "金额必须大于 0")
    private BigDecimal amount;

    @NotNull(message = "交易时间不能为空")
    private LocalDateTime transactionTime;

    @Size(max = 255, message = "备注长度不能超过 255")
    private String remark;
}
