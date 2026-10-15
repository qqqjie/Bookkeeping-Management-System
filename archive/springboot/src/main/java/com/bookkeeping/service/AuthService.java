package com.bookkeeping.service;

import com.bookkeeping.dto.LoginRequest;
import com.bookkeeping.dto.LoginResponse;
import com.bookkeeping.dto.RegisterRequest;

public interface AuthService {

    LoginResponse register(RegisterRequest request);

    LoginResponse login(LoginRequest request);
}
