#!/bin/sh

python ../main.py --gen-code --full-export --export config.cfg

python ../main.py --full-export --export config2.cfg

python ../main.py --full-export --export config3.cfg
