#!/usr/bin/bash

if [ ! -d "proto/python_out" ]; then
    mkdir -p proto/python_out
fi

for file in `ls -a proto`
    do
        if echo ${file} | grep -q -E '\.proto$'
            then
                echo -e \\033[32m [√] Generate message type for ${file} \\033[0m
                protoc -I=proto --python_out=proto/python_out proto/${file}
        fi
done

cd proto/python_out
sed -i -E 's/^import.*_pb2/from . \0/' *.py
cd ../../
