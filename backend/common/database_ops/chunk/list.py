async def list_get_chunks(
    conn,
    chunk_table_name: str,
):
    rows = await conn.fetch(
        f"""
        SELECT chunk_id, text, metadata, text_bytes, embedding_bytes FROM {chunk_table_name}
    """
    )
    results = [
        {
            "chunk_id": row["chunk_id"],
            "text": row["text"],
            "metadata": row["metadata"],
            "text_bytes": row["text_bytes"],
            "embedding_bytes": row["embedding_bytes"],
        }
        for row in rows
    ]
    return results


async def list_get_record_chunks(conn, chunk_table_name: str, record_id: str):
    rows = await conn.fetch(
        f"""
        SELECT chunk_id, text, metadata, text_bytes, embedding_bytes FROM {chunk_table_name}
        WHERE record_id = $1
    """,
        record_id,
    )
    results = [
        {
            "chunk_id": row["chunk_id"],
            "text": row["text"],
            "metadata": row["metadata"],
            "text_bytes": row["text_bytes"],
            "embedding_bytes": row["embedding_bytes"],
        }
        for row in rows
    ]
    return results
