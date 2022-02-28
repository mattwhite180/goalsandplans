echo 'starting taskify...'
while [ true ]
do
    sleep 900
    python3 manage.py taskify
    echo "ran taskify"
done
