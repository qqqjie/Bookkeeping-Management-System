package com.bookkeeping.common;

import com.baomidou.mybatisplus.core.metadata.IPage;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.function.Function;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class PageVO<T> {

    private List<T> records;

    private long total;

    private long page;

    private long size;

    private long pages;

    public static <E, T> PageVO<T> from(IPage<E> page, Function<E, T> converter) {
        List<T> records = page.getRecords().stream().map(converter).toList();
        return new PageVO<>(records, page.getTotal(), page.getCurrent(), page.getSize(), page.getPages());
    }
}
