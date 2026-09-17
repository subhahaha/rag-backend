import redis

from app.config import REDIS_HOST, REDIS_PORT


redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True
)

def save_message(
    conversation_id: str,
    role: str,
    content: str
) -> None:
    key = f"chat:{conversation_id}"

    redis_client.rpush(
        key,
        f"{role}: {content}"
    )


def get_messages(conversation_id: str) -> list[str]:
    key = f"chat:{conversation_id}"

    return redis_client.lrange(key, 0, -1)


def clear_messages(conversation_id: str) -> None:
    key = f"chat:{conversation_id}"

    redis_client.delete(key)

def save_booking_field(
    conversation_id: str,
    field: str,
    value: str,
) -> None:
    key = f"booking:{conversation_id}"

    redis_client.hset(
        key,
        field,
        value,
    )


def get_booking_data(
    conversation_id: str,
) -> dict[str, str]:
    key = f"booking:{conversation_id}"

    return redis_client.hgetall(key)


def clear_booking_data(
    conversation_id: str,
) -> None:
    key = f"booking:{conversation_id}"

    redis_client.delete(key)