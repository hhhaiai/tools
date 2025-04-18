#!/bin/bash

###1. 获取安装列表通过adb shell pm list packages获取包名列表,去掉每行开头的package:字段
packages=$(adb shell pm list packages | sed 's/package://g')
# 按行分隔成数组
installed_array=($packages)

### 2.遍历文件夹下文件名
for file in ./*; do
    ### 3. 遍历是名字
    if test -f $file; then
        # 4. 判断文件后缀
        if echo "$file" | grep -q -E '\.apk$'; then
            #echo "$file"
            ## 5. 获取包名,方案1
            # str=$(echo $file)
            # array=(${str//-/ })
            # appname=${array[0]}
            # pkg=${array[1]}
            # appname=$(echo "$appname" | sed 's/.\///g')
            if [[ $file =~ ^.*/(.*)-(.*)-(.*)\.apk$ ]]; then
                appname=${BASH_REMATCH[1]}
                pkg=${BASH_REMATCH[2]}
                version=${BASH_REMATCH[3]}
            fi
            ### 6. 判断没有安装的才进行安装
            ## 方案一
            # if ! [[ ${installed_array[*]} =~ $pkg ]]; then
            #     echo "____[$appname] 未安装,即将进行安装~"
            #     adb install -r -t -g $file
            # fi
            ## 方案二
            if [[ ! ${installed_array[*]} =~ ${pkg} ]]; then
                # 安装逻辑
                echo "____[$appname] 未安装,即将进行安装~"
                adb install -r -t -g $file
            else
                echo "[$appname] 已经安装..."
            fi
        fi
    fi
done
