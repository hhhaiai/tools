#!/bin/bash

# 备份目录
BACKUP_DIR="backup_apks"
mkdir -p "$BACKUP_DIR"

# 获取所有第三方应用包名
echo "获取第三方应用列表..."
packages=$(adb shell pm list packages -3 | sed 's/package://g')

# 遍历每个包名
for package in $packages; do
    echo "正在处理应用: $package"
    
    # 获取 APK 路径
    apk_path=$(adb shell pm path "$package" | head -n 1 | sed 's/package://g')

    if [ -n "$apk_path" ]; then
        # 备份 APK，文件名使用包名
        output_file="$BACKUP_DIR/${package}.apk"
        echo "备份: $apk_path -> $output_file"
        adb pull "$apk_path" "$output_file"
    else
        echo "未找到 $package 的 APK 文件，跳过。"
    fi
done

echo "备份完成，APK 存放于 $BACKUP_DIR 目录中。"