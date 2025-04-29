#!/bin/bash

__usage="
Usage: $(basename $0) [OPTIONS]

Run API server for hmTracker.
By default secrets and configs are defined in ressources/.env file

Options:
  -p, --production             Run the API server in production mode
  -h, --help                   print this help
"

## === DEFAULT VALUES ==== 

BASEDIR=$(dirname $0)
RESSOURCE_DIR="$BASEDIR/backend/resources/"
SOURCE_DIR="$BASEDIR/backend/src/"
SECRETS="$RESSOURCE_DIR/.env"

## === ARGUMENT PARSING ==== 
while test $# -gt 0
do
    case "$1" in
        -h) PRINT_HELP=1
            ;;
        --help) PRINT_HELP=1
            ;;
        -p) RUN_PROD=1
            ;;
        --production) RUN_PROD=1
            ;;
        
        --*) echo "bad option : $1";PRINT_HELP=1
            ;;
        *)
            echo "bad argument : $1";PRINT_HELP=1
            ;;
    esac
    shift
done


if [ ! -z "$PRINT_HELP" ];
then
    echo "$__usage";
    exit 0;
fi

## === MAIN ==== 

export PYTHON_PATH="${PYTHONPATH}:${SOURCE_DIR}"
set -a
source $SECRETS
set +a

if [ ! -z  "$RUN_PROD" ];
then
    fastapi run $SOURCE_DIR/hmtracker/api/server.py ;
else
    fastapi dev $SOURCE_DIR/hmtracker/api/server.py ;
fi
exit 0;