# goalsandplans

## See it live on http://goalsandplans101.com

## Use public docker repo
Here is a `docker-compose.yaml` example:
```
version: "3.3"

services:
  server:
    restart: always
    image: public.ecr.aws/z7r6z9m1/goalsandplans:latest
    command: bash django-run.sh
    volumes:
      - "~/.aws:/root/.aws"
    env_file:
        - secrets.env
    expose:
      - "8000"
    ports:
      - "8000:8000"
```

## [optional] setup secrets for AWS RDS connectivity
* create a `secrets.env` file in the root directory of project
* fill out the folling with your own variables:
*   ```
    SECRET=your-aws-secret-name
    REGION=your-aws-region
    ```
