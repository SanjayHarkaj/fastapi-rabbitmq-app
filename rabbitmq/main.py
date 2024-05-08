import json
from aio_pika import connect_robust, Message, RobustConnection
from config import RABBITMQ_URL


async def get_rabbitmq_connection():
    return await connect_robust(RABBITMQ_URL)


async def publish_on_queue(queue, data):
    rabbitmq_connection: RobustConnection = get_rabbitmq_connection()
    connection = await rabbitmq_connection  # Await the coroutine
    async with connection as rabbitmq_connection:
        channel = await rabbitmq_connection.channel()
        await channel.default_exchange.publish(
            Message(body=data.encode()),
            routing_key=queue
        )


async def consume_from_queue(queue, func):
    connection = await connect_robust(RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()
        data = await channel.declare_queue(queue)

        async for message in data:
            async with message.process():
                data = json.loads(message.body.decode())
                await func(data)
