package com.bookkeeping.service.impl;

import com.bookkeeping.dto.LoginRequest;
import com.bookkeeping.dto.LoginResponse;
import com.bookkeeping.dto.RegisterRequest;
import com.bookkeeping.entity.User;
import com.bookkeeping.exception.BusinessException;
import com.bookkeeping.exception.ErrorCode;
import com.bookkeeping.security.JwtUtil;
import com.bookkeeping.service.AuthService;
import com.bookkeeping.service.UserService;
import com.bookkeeping.vo.UserVO;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.authentication.DisabledException;
import org.springframework.security.authentication.LockedException;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.AuthenticationException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class AuthServiceImpl implements AuthService {

    private final UserService userService;

    private final AuthenticationManager authenticationManager;

    private final JwtUtil jwtUtil;

    @Override
    @Transactional
    public LoginResponse register(RegisterRequest request) {
        if (userService.existsByUsername(request.getUsername())) {
            throw new BusinessException(ErrorCode.CONFLICT, "用户名已被注册");
        }
        if (userService.existsByEmail(request.getEmail())) {
            throw new BusinessException(ErrorCode.CONFLICT, "邮箱已被注册");
        }
        User user = userService.createUser(
                request.getUsername(),
                request.getEmail(),
                request.getPassword(),
                request.getNickname());
        return buildLoginResponse(user);
    }

    @Override
    public LoginResponse login(LoginRequest request) {
        try {
            authenticationManager.authenticate(new UsernamePasswordAuthenticationToken(
                    request.getLoginId(), request.getPassword()));
        } catch (BadCredentialsException | DisabledException | LockedException ex) {
            throw new BusinessException(ErrorCode.UNAUTHORIZED, "登录账号或密码错误");
        } catch (AuthenticationException ex) {
            throw new BusinessException(ErrorCode.UNAUTHORIZED, "登录失败，请稍后重试");
        }
        User user = userService.getByLoginId(request.getLoginId());
        return buildLoginResponse(user);
    }

    private LoginResponse buildLoginResponse(User user) {
        String token = jwtUtil.generateToken(user.getUserId(), user.getUsername());
        return new LoginResponse(token, UserVO.from(user));
    }
}
