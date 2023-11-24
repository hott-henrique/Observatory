import os
import numpy as np

import qdrant_client as qdrant

from qdrant_client import models


qdrant_client = qdrant.QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
)

try:
    qdrant_client.create_collection(collection_name="NewsEmbeddings",
                                    vectors_config=models.VectorParams(size=768,
                                                                       distance=models.Distance.COSINE,
                                                                       on_disk=True),
                                    on_disk_payload=True)
except: pass

qdrant_client.upsert(collection_name="NewsEmbeddings",
                     points=[ models.PointStruct(id="5c56c793-69f3-4fbf-87e6-c4bf54c28c25", vector=list(np.random.random(size=768)))])

qdrant_client.close()

