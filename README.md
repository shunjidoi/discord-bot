### How to deploy

```
docker-compose run --rm pipenv pipenv install --dev
open devcontainer

sam build
sam deploy --profile xx --guided
```

### Trouble shooting
bash: python: command not found

```
$ echo $PATH
/workspace/.venv/bin:
# why need?
export PATH=$PATH:/workspace/discord-bot/.venv/bin/
```

AmazonEC2FullAccess	 が必要
