APPNAME=turk
APPDIR=/home/ec2-user/rec_table/web/$APPNAME/

LOGFILE=$APPDIR'gunicorn.log'
ERRORFILE=$APPFIR'gunicorn-error.log'

NUM_WORKERS=3

ADDRESS=172.31.20.32:8000

cd $APPDIR

source ~/.bashrc

exec gunicorn $APPNAME.wsgi:application \
-w $NUM_WORKERS --bind=$ADDRESS \
--log-level=debug \
--log-file=$LOGFILE 2>>$LOGFILE  1>>$ERRORFILE &
