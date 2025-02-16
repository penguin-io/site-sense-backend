import asyncio
import json
import meilisearch
from aiokafka import AIOKafkaConsumer

KAFKA_BROKER = "localhost:9092"
KAFKA_TOPIC = "attendance_logs"
MEILISEARCH_URL = "http://127.0.0.1:7700"
MEILISEARCH_INDEX = "logs"
MEILISEARCH_API_KEY = "myKey"

# Connect to Meilisearch
client = meilisearch.Client(MEILISEARCH_URL, MEILISEARCH_API_KEY)

# Create index if not exists
client.index(MEILISEARCH_INDEX).update_settings({"sortableAttributes": ["timestamp"]})


async def consume_logs():
    consumer = AIOKafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )
    await consumer.start()
    try:
        async for msg in consumer:
            log = msg.value
            client.index(MEILISEARCH_INDEX).add_documents(
                [log]
            )  # Store log in Meilisearch
            print("Log indexed:", log)
    finally:
        await consumer.stop()
