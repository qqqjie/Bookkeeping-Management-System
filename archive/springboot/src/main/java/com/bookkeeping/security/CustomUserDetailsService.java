package com.bookkeeping.security;

import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import com.bookkeeping.entity.User;
import com.bookkeeping.mapper.UserMapper;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class CustomUserDetailsService implements UserDetailsService {

    private final UserMapper userMapper;

    public CustomUserDetailsService(UserMapper userMapper) {
        this.userMapper = userMapper;
    }

    @Override
    public UserDetails loadUserByUsername(String loginId) throws UsernameNotFoundException {
        List<User> users = userMapper.selectList(Wrappers.<User>lambdaQuery()
                .and(wrapper -> wrapper.eq(User::getUsername, loginId)
                        .or()
                        .eq(User::getEmail, loginId))
                .last("LIMIT 1"));
        if (users.isEmpty()) {
            throw new UsernameNotFoundException("用户不存在: " + loginId);
        }
        return new LoginUser(users.get(0));
    }
}
