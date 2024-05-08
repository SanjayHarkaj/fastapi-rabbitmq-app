# JWT configs
SECRET_KEY = "aidhere_project"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 3000

# RabbitMQ Configs
REQUEST_LINK_QUEUE = 'request_link_queue'
ACCESS_TOKEN_QUEUE = 'access_token_queue'
RABBITMQ_URL = 'amqp://guest:guest@localhost/'
