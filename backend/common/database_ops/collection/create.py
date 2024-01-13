from common.models import Collection, TextSplitter, Status
from .get import get_collection
from typing import Dict
import json
import logging

logger = logging.getLogger(__name__)


async def create_collection(
    postgres_conn,
    name: str,
    description: str,
    capacity: int,
    embedding_model_id: str,
    embedding_size: int,
    text_splitter: TextSplitter,
    metadata: Dict[str, str],
) -> Collection:
    """
    Create collection
    :param postgres_conn: postgres connection
    :param name: the collection name
    :param description: the collection description
    :param capacity: the collection capacity
    :param embedding_model_id: the embedding model id
    :param embedding_size: the embedding size
    :param text_splitter: the text splitter
    :param metadata: the collection metadata
    :return: the created collection
    """

    new_id = Collection.generate_random_id()

    async with postgres_conn.transaction():
        # 1. insert the collection into database
        await postgres_conn.execute(
            """
            INSERT INTO collection (collection_id, name, description, capacity,
            embedding_model_id, embedding_size, text_splitter, status, metadata)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """,
            new_id,
            name,
            description,
            capacity,
            embedding_model_id,
            embedding_size,
            text_splitter.model_dump_json(),
            Status.READY.value,
            json.dumps(metadata),
        )

        chunk_table_name = Collection.get_chunk_table_name(new_id)
        create_chunk_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {chunk_table_name} (
                chunk_id CHAR(24) NOT NULL PRIMARY KEY,
                record_id CHAR(24) NOT NULL REFERENCES record (record_id) ON DELETE CASCADE,
                content TEXT NOT NULL,
                metadata JSONB NOT NULL DEFAULT '{{}}',
                embedding vector({embedding_size}) NOT NULL,
                updated_timestamp BIGINT NOT NULL,
                created_timestamp BIGINT NOT NULL
            );
        """

        logging.debug(f"create_collection: create chunk table with: \n {create_chunk_table_sql}")

        # 2. create the chunk table
        await postgres_conn.execute(create_chunk_table_sql)

        # 3. todo: add index

    # 3. get and add to redis
    collection = await get_collection(postgres_conn, new_id)
    return collection
