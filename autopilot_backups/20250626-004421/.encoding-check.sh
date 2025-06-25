#!/bin/bash
# 编码诊断工具
echo "=== 系统编码检测 ==="
echo "LANG: $LANG"
echo "LC_ALL: $LC_ALL"
echo ""

echo "=== 文件编码检测 ==="
for file in modules/*.py; do
  encoding=$(file -bi "$file" | awk -F'=' '{print $2}')
  line_endings=$(file "$file" | grep -o 'with CRLF line terminators')
  printf "%-20s %-15s %s\n" "$file" "$encoding" "${line_endings:-LF line terminators}"
done

echo ""
echo "=== 修复建议 ==="
echo "1. 统一使用UTF-8编码:"
echo "   find . -type f -name '*.py' -exec sed -i 's/\r$//' {} \;"
echo "2. 设置终端编码:"
echo "   chcp 65001  # Windows代码页设置为UTF-8"
echo "3. 配置Git自动转换:"
echo "   git config --global core.autocrlf input"