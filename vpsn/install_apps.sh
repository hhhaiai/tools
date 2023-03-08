#!/bin/bash
# 1.遍历文件夹下文件名
for file in ./*; do
    # 2. 遍历是名字
    if test -f $file; then
        #    echo $file 是文件
        # 3.判断文件后缀
        if echo "$file" | grep -q -E '\.apk$'; then
            echo "will install $file"
            adb install -r -t -g $file
        fi
    fi
done
