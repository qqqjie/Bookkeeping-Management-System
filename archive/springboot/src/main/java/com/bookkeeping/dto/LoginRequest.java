package com.bookkeeping.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class LoginRequest {

    @NotBlank(message = "登录账号不能为空")
    private String loginId;

    @NotBlank(message = "密码不能为空")
    private String password;
}
