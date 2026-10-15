package com.bookkeeping.vo;

import com.bookkeeping.entity.User;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class UserVO {

    private Long userId;

    private String username;

    private String email;

    private String nickname;

    private Integer status;

    private LocalDateTime createdAt;

    public static UserVO from(User user) {
        return new UserVO(
                user.getUserId(),
                user.getUsername(),
                user.getEmail(),
                user.getNickname(),
                user.getStatus(),
                user.getCreatedAt());
    }
}
