package com.bookkeeping.service;

import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import com.bookkeeping.dto.UserUpdateRequest;
import com.bookkeeping.entity.User;
import com.bookkeeping.exception.BusinessException;
import com.bookkeeping.exception.ErrorCode;
import com.bookkeeping.mapper.UserMapper;
import com.bookkeeping.vo.UserVO;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;

import java.util.List;

@Service
@RequiredArgsConstructor
public class UserServiceImpl implements UserService {

    private final UserMapper userMapper;

    private final PasswordEncoder passwordEncoder;

    @Override
    public User getById(Long userId) {
        User user = userMapper.selectById(userId);
        if (user == null) {
            throw new BusinessException(ErrorCode.NOT_FOUND, "用户不存在");
        }
        return user;
    }

    @Override
    public User getByLoginId(String loginId) {
        List<User> users = userMapper.selectList(Wrappers.<User>lambdaQuery()
                .and(wrapper -> wrapper.eq(User::getUsername, loginId)
                        .or()
                        .eq(User::getEmail, loginId))
                .last("LIMIT 1"));
        if (users.isEmpty()) {
            throw new BusinessException(ErrorCode.NOT_FOUND, "用户不存在");
        }
        return users.get(0);
    }

    @Override
    public boolean existsByUsername(String username) {
        return userMapper.selectCount(Wrappers.<User>lambdaQuery()
                .eq(User::getUsername, username)) > 0;
    }

    @Override
    public boolean existsByEmail(String email) {
        return userMapper.selectCount(Wrappers.<User>lambdaQuery()
                .eq(User::getEmail, email)) > 0;
    }

    @Override
    @Transactional
    public User createUser(String username, String email, String rawPassword, String nickname) {
        User user = new User();
        user.setUsername(username);
        user.setEmail(email);
        user.setPasswordHash(passwordEncoder.encode(rawPassword));
        user.setNickname(StringUtils.hasText(nickname) ? nickname : username);
        user.setStatus(1);
        userMapper.insert(user);
        return user;
    }

    @Override
    public UserVO getProfile(Long userId) {
        return UserVO.from(getById(userId));
    }

    @Override
    @Transactional
    public UserVO updateProfile(Long userId, UserUpdateRequest request) {
        User user = getById(userId);
        if (StringUtils.hasText(request.getEmail()) && !request.getEmail().equals(user.getEmail())) {
            if (existsByEmail(request.getEmail())) {
                throw new BusinessException(ErrorCode.CONFLICT, "邮箱已被使用");
            }
            user.setEmail(request.getEmail());
        }
        if (StringUtils.hasText(request.getNickname())) {
            user.setNickname(request.getNickname());
        }
        userMapper.updateById(user);
        return UserVO.from(user);
    }
}
