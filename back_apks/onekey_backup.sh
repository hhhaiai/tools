#!/bin/bash
# 自动导出Android设备第三方APK的脚本[1,7](@ref)

# 步骤1：获取所有第三方包名列表
packages=$(adb shell pm list packages -3 | cut -d':' -f2)

# 创建存储目录（按时间戳命名）
folder_name="apk_export_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$folder_name"

# 步骤2：遍历每个包名
for pkg in $packages; do
    echo "正在处理包: $pkg"

    # 获取APK路径（过滤空行和错误输出）
    apk_path=$(adb shell pm path "$pkg" 2>/dev/null | grep -v '^$' | head -1 | cut -d':' -f2)

    if [ -z "$apk_path" ]; then
        echo "⚠️  未找到APK路径: $pkg"
        continue
    fi

    # 步骤3：导出APK到本地
    adb pull "$apk_path" "$folder_name/${pkg}.apk"

    # 校验导出结果
    if [ $? -eq 0 ]; then
        echo "✅ 导出成功: $pkg.apk"
    else
        echo "❌ 导出失败: $pkg"
    fi
done

echo "操作完成，APK已保存至: $folder_name/"