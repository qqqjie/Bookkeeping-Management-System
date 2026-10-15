package com.bookkeeping.service;

import com.bookkeeping.dto.UserUpdateRequest;
import com.bookkeeping.entity.User;
import com.bookkeeping.vo.UserVO;

public interface UserService {

    User getById(Long userId);

    User getByLoginId(String loginId);

    boolean existsByUsername(String username);

    boolean existsByEmail(String email);

    User createUser(String username, String email, String rawPassword, String nickname);

    UserVO getProfile(Long userId);

    UserVO updateProfile(Long userId, UserUpdateRequest request);
}
