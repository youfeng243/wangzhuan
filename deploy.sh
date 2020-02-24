#!/usr/bin/env bash

set -e

unset all_proxy && unset ALL_PROXY

pip install --user virtualenv==16.4.3 -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
home=`pwd`
rm -rf venv
echo "deploy path ${home}"
virtualenv ${home}/venv --python=python3 --no-setuptools
${home}/venv/bin/pip install Cython==0.28.3 -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
${home}/venv/bin/pip install setuptools==39.1.0 -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
${home}/venv/bin/pip install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
echo "deploy finish"