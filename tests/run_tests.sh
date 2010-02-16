#!/bin/sh

export PYTHONPATH=..

cd `pwd`/`dirname $0`

python test_api.py
python test_import.py
python ulp/test_basic.py
