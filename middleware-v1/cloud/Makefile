# -*- coding: utf-8 -*-
.ONESHELL:
SHELL = /bin/bash

install:
	tfswitch

init:
	terraform init

uat: install init
	terraform workspace select uat || terraform workspace new uat
	terraform apply -var-file vars/uat/common.tfvars

pprod: install init
	terraform workspace select pprod || terraform workspace new pprod
	terraform apply -var-file vars/pprod/common.tfvars

prod: install init
	terraform workspace select prod || terraform workspace new prod
	terraform apply -var-file vars/prod/common.tfvars
