#!bin/sh

env="venv"

if [ -d $env" ]; then
    rm -rf $env
fi

python3 -m venv $env --system-site-packages
source $env/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
deactivate
