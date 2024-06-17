.ONESHELL:
SHELL = /bin/bash

install:
	@echo "# - Installing serverless plugins"
	serverless plugin install -n serverless-python-requirements

uat: install
	@echo "# - Deploying uat environnment"
	serverless deploy --stage uat
	@echo "# - Deployed uat environnment"

prod: install
	@echo "# - Deploying prod environnment"
	serverless deploy --stage prod
	@echo "# - Deployed prod environnment"
