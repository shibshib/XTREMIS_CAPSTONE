#!/bin/bash    
HOST="freudenreich.ca:32768"
FTPURL="ftp://$HOST"
LCD="./Data"
RCD="."
DELETE="--delete"
lftp -c "set ftp:list-options -a;
    open '$FTPURL';
    lcd $LCD;
    cd $RCD;
    mirror --verbose \
    --exclude-glob pypdf.zip
    --exclude-glob *.mp4
    --exclude-glob *.bdf"
    
