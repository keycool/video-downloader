#!/bin/bash
# 自动清理临时文件的脚本
# 当 tmpclaude-* 文件超过 3 个时自动清理

# 设置工作目录
WORK_DIR="$(pwd)"

# 计算 tmpclaude-* 文件数量
TEMP_FILE_COUNT=$(find "$WORK_DIR" -maxdepth 1 -name "tmpclaude-*" -type f 2>/dev/null | wc -l)

echo "检测到 $TEMP_FILE_COUNT 个临时文件"

# 如果超过 3 个，则清理
if [ "$TEMP_FILE_COUNT" -gt 3 ]; then
    echo "临时文件数量超过 3 个，开始清理..."

    # 删除所有 tmpclaude-* 文件
    find "$WORK_DIR" -maxdepth 1 -name "tmpclaude-*" -type f -delete

    # 再次统计确认
    REMAINING_COUNT=$(find "$WORK_DIR" -maxdepth 1 -name "tmpclaude-*" -type f 2>/dev/null | wc -l)

    echo "✅ 清理完成！删除了 $((TEMP_FILE_COUNT - REMAINING_COUNT)) 个临时文件"
else
    echo "临时文件数量未超过阈值，无需清理"
fi
