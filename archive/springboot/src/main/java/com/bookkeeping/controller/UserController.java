package com.bookkeeping.controller;

import com.bookkeeping.common.Result;
import com.bookkeeping.dto.UserUpdateRequest;
import com.bookkeeping.security.SecurityUtils;
import com.bookkeeping.service.UserService;
import com.bookkeeping.vo.UserVO;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/users")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @GetMapping("/me")
    public Result<UserVO> getCurrentUserProfile() {
        return Result.success(userService.getProfile(SecurityUtils.getCurrentUserId()));
    }

    @PutMapping("/me")
    public Result<UserVO> updateCurrentUserProfile(@Valid @RequestBody UserUpdateRequest request) {
        return Result.success(userService.updateProfile(SecurityUtils.getCurrentUserId(), request));
    }
}
