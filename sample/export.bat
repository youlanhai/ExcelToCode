@echo off

python ..\main.py --gen-code --export --full-export --encode-log config.cfg
python ..\main.py --gen-code --export --full-export --encode-log config2.cfg
python ..\main.py --gen-code --export --full-export --encode-log config3.cfg

pause
