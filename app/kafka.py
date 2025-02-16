from aiokafka import AIOKafkaProducer
import json
import asyncio

KAFKA_BROKER = "localhost:9092"  # Change if Kafka is on a different machine
KAFKA_TOPIC = "attendance_logs"

producer = None  # Global producer instance


async def get_kafka_producer():
    global producer
    if producer is None:
        producer = AIOKafkaProducer(
            bootstrap_servers=KAFKA_BROKER,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        await producer.start()
    return producer


async def send_log_to_kafka(log_data):
    producer = await get_kafka_producer()
    await producer.send(KAFKA_TOPIC, log_data)
