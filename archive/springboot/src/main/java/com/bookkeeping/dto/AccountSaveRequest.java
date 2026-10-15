package com.bookkeeping.dto;

import com.bookkeeping.enums.AccountType;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import lombok.Data;

import java.math.BigDecimal;

@Data
public class AccountSaveRequest {

    @NotBlank(message = "账户名称不能为空")
    @Size(max = 50, message = "账户名称长度不能超过 50")
    private String accountName;

    @NotNull(message = "账户类型不能为空")
    private AccountType accountType;

    @Pattern(regexp = "^[A-Z]{3}$", message = "币种须为三位大写字母，如 CNY")
    private String currency;

    @DecimalMin(value = "0.00", message = "初始余额不能为负数")
    private BigDecimal initialBalance;

    @Min(value = 0, message = "includeInTotal 只能为 0 或 1")
    @Max(value = 1, message = "includeInTotal 只能为 0 或 1")
    private Integer includeInTotal;
}
