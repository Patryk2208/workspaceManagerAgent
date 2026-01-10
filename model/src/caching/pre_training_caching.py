import redis
import numpy as np
from sympy.strategies.branch.traverse import top_down


class PreTrainingCaching:
    def __init__(self, host, port, db, password):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.redis_client = redis.Redis(
            host=self.host,
            port=self.port,
            db=self.db,
            password=self.password,
            decode_responses=False
        )
        self.embedding_dimension = 384
        self.embedding_dtype = "float32"

    def populate_window_titles_batch(self, window_titles_batch : list[str], window_title_embeddings_batch : np.ndarray):
        with self.redis_client.pipeline() as pipe:
            i = 0
            for window_title in window_titles_batch:
                pipe.set(window_title, window_title_embeddings_batch[i].tobytes())
                i += 1
        #todo
        pass
