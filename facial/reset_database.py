from qdrant_client import QdrantClient, models

if __name__ == '__main__':
    # Init qdrant client
    with open('qdrant_key.txt', 'r') as f:
        hostname = f.readline().rstrip()
        key = f.readline().rstrip()

    qdrant_client = QdrantClient(host=hostname,
                                 api_key=key)

    if (qdrant_client.recreate_collection(
        collection_name='faces',
        vectors_config=models.VectorParams(size=128,
                                           distance=models.Distance.EUCLID))):
        print('Database reset successfully')
    else:
        print('Error resetting database')