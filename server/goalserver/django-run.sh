#!/bin/bash

FILE=djangosecret.txt

if [ -f "$FILE" ]; then
    echo $FILE "exists."
else 
    echo "$FILE does not exist."
    python3 create-secret.py > $FILE
    echo "created $FILE"
fi

hostname -I
hostname -I
hostname -I
hostname -I
hostname -I
hostname -I
hostname -I
echo 'sleeping for 5'
sleep 5
echo 'done sleeping. running migrations'
python3 manage.py makemigrations planapp && \
python3 manage.py makemigrations
python3 manage.py makemigrations && \
python3 manage.py migrate && \
echo 'done with migrations. running server'
python3 manage.py runserver 0:8000
