#!/bin/bash

for file in ./*; do
    if test -f $file; then
        if echo "$file" | grep -q -E '\.apk$'; then
            echo "$file"

            if [[ $file =~ ^.*/(.*)-(.*)-(.*)\.apk$ ]]; then
                appname=${BASH_REMATCH[1]}
                pkg=${BASH_REMATCH[2]}
                version=${BASH_REMATCH[3]}
            fi
            echo "appname: $appname"
            echo "pkg: $pkg"
            echo "version: $version"
        fi
    fi
done
