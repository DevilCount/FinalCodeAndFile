package com.sunyaxin.common.result;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;
import java.util.List;

/**
 * 分页结果
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class PageResult<T> implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 当前页码
     */
    private Long current;

    /**
     * 每页条数
     */
    private Long size;

    /**
     * 总记录数
     */
    private Long total;

    /**
     * 总页数
     */
    private Long pages;

    /**
     * 数据列表
     */
    private List<T> records;

    /**
     * 是否有上一页
     */
    private Boolean hasPrevious;

    /**
     * 是否有下一页
     */
    private Boolean hasNext;

    /**
     * 构建分页结果
     */
    public static <T> PageResult<T> of(Long current, Long size, Long total, List<T> records) {
        PageResult<T> result = new PageResult<>();
        result.setCurrent(current);
        result.setSize(size);
        result.setTotal(total);
        result.setRecords(records);
        
        // 计算总页数
        long pages = total / size;
        if (total % size != 0) {
            pages++;
        }
        result.setPages(pages);
        
        // 是否有上一页
        result.setHasPrevious(current > 1);
        
        // 是否有下一页
        result.setHasNext(current < pages);
        
        return result;
    }

    /**
     * 构建空分页结果
     */
    public static <T> PageResult<T> empty(Long current, Long size) {
        return of(current, size, 0L, List.of());
    }
}
