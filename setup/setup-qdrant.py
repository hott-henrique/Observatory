import os

import qdrant_client as qdrant

from qdrant_client import models


qdrant_client = qdrant.QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_TOKEN"),
)

try:
    qdrant_client.create_collection(collection_name="NewsEmbeddings",
                                    vectors_config=models.VectorParams(size=768,
                                                                       distance=models.Distance.COSINE,
                                                                       on_disk=True),
                                    on_disk_payload=True)
except: pass

qdrant_client.close()

