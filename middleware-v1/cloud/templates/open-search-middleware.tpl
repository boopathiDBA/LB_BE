[
  {
    "name": "open-search-cerebro",
    "image": "${REGISTRY_IMAGE}",
    "networkMode": "awsvpc",
    "essential": true,
    "pseudoTerminal": true,
    "interactive": true,
    "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-create-group": "true",
          "awslogs-group": "${CLOUDWATCH_LOG_NAME}",
          "awslogs-stream-prefix": "svc-${CONTAINER_NAME}",
          "awslogs-region": "${AWS_REGION}"
        }
    },
    "environment": ${jsonencode(MAPAS)},
    "portMappings": ${jsonencode(PORTMAPPING)},
    "ulimits": [
      {
          "name": "nofile",
          "softLimit": 65536,
          "hardLimit": 65536
       }
     ]
  }
]
