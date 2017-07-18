#!/bin/bash

# Application Name
NAME="instagram"                             	 #Name of the application (*)
DJANGODIR=/home/ubuntu/instagram/instagram	 # Django project directory (*)
#SOCKFILE=/var/www/test/run/gunicorn.sock        # we will communicate using this unix socket (*)
USER=ubuntu                                      # the user to run as (*)
NUM_WORKERS=3                                    # how many worker processes should Gunicorn spawn (*)

# Which settings file should Django use
DJANGO_SETTINGS_MODULE=shoppr_instagram.settings
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE

# Django project directory
DJANGO_WSGI_MODULE=shoppr_instagram.wsgi

# Host
HOST=127.0.0.1
PORT=8002

echo "Starting $APP_NAME as `whoami`"

# Activate the virtual environment
cd $DJANGO_DIR
source ../bin/activate
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
exec ../bin/gunicorn $DJANGO_WSGI_MODULE:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --user=$USER \
  --bind=$HOST:$PORT \
  --log-level=debug \
  --log-file=-

