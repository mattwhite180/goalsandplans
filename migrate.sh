docker exec -it goalsandplans_server_1 python3 manage.py clear_cache
docker exec -it goalsandplans_server_1 python3 manage.py clean_pyc
docker exec -it goalsandplans_server_1 python3 manage.py reset_schema
docker exec -it goalsandplans_server_1 python3 manage.py reset_db
docker exec -it goalsandplans_server_1 python3 manage.py migrate auth
docker exec -it goalsandplans_server_1 python3 manage.py makemigrations
docker exec -it goalsandplans_server_1 python3 manage.py migrate
