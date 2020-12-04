#!/bin/bash

################################################################################################################################

function echo_red(){           #echo in red (for ease of vgrep)
  echo -en "\033[31m"
  echo "$1"
  echo -en "\033[0m"
}
function echo_green(){         #echo in green
  echo -en "\033[32m"
  echo "$1"
  echo -en "\033[0m"
}
function echo_blue(){          #echo in blue (for ease of vgrep)
  echo -en "\033[34m"
  echo "$1"
  echo -en "\033[0m"
}
function error_check(){        #Print green OK or red error and exit.
  if [ $1 == 0 ]; then
    echo_green "OK"; echo ""
  else
    echo_red   "Failed, with error code $1"; echo ""
    exit 1
  fi
}

################################################################################################################################

repo_name="Django-Showcase"
vir_env_dir=".Venv-${repo_name}"

################################################################################################################################

[ -d ${vir_env_dir} ] || python3 -m venv ${vir_env_dir}
source ${vir_env_dir}/bin/activate ; error_check $?
pip  install --upgrade pip         ; error_check $?
pip3 install -r requirements.txt   ; error_check $?

if [ -f mysite/mysite/settings.py ]; then 
    [ -f mysite/mysite/secrets.py ] || {
        secret_key=$(
            python -c 'import random; print("".join([random.choice("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)") for i in range(50)]))'
        )
        echo "SECRET_KEY = '${secret_key}'" > mysite/mysite/secrets.py
        error_check $?
    }
fi
cd ~/Git-Repos/${repo_name}/mysite/
python manage.py makemigrations capitalcallapp
python manage.py migrate

exit 0

echo "The following commands might be useful:

source .Venv-Django-Showcase/bin/activate
python mysite/manage.py makemigrations capitalcallapp
python mysite/manage.py migrate
python mysite/manage.py runserver &
python mysite/manage.py runserver
git status
git add -A
git commit -m \"REMEMBER TO ADD A COMMIT MESSAGE\!\"  
git push origin master

"

################################################################################################################################


