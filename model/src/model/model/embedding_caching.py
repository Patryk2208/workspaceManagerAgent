import numpy as np
import redis
import os
import hashlib


class EmbeddingCaching:
    def __init__(self):
        """
        redis client for caching window descriptions' embeddings.
        """
        self.host = os.environ.get("REDIS_HOST", "localhost")
        self.port = os.environ.get("REDIS_PORT", "6379")
        self.db = os.environ.get("REDIS_DB", 0)
        self.password = os.environ.get("REDIS_PASSWORD", None)
        self.redis_client = redis.Redis(
            host=self.host,
            port=self.port,
            db=0,
            password=self.password,
            decode_responses=False
        )
        self.embedding_dimension = 384
        self.embedding_dtype = np.float32

    def _test_connection(self):
        """
        tests connection to the redis server.
        :return: True if connection is successful, False otherwise.
        """
        try:
            self.redis_client.ping()
            return True
        except redis.exceptions.ConnectionError:
            return False

    @staticmethod
    def _get_key_hash(sentence : str) -> str:
        """
        generates sha256 hash of the sentence for better hashmap performance.
        :param sentence:
        :return: hashed sentence.
        """
        return hashlib.sha256(sentence.encode()).hexdigest()

    def try_get_cache_hit(self, sentence : str) -> np.ndarray | None:
        """
        checks if the sentence is already cached in the cache.
        :param sentence:
        :return: cached embedding if successful, None otherwise.
        """
        try:
            key = self._get_key_hash(sentence)
            cached_embedding = self.redis_client.get(key)
            if cached_embedding is not None:
                return np.frombuffer(cached_embedding, dtype=self.embedding_dtype)
            else:
                return None
        except Exception as e:
            print(f"Failed to cache sentence: {e}")
            return None

    def try_get_cache_hit_batch(self, sentences : list[str]) -> list[np.ndarray] | None:
        """
        checks what sentences are already cached in the cache.
        :param sentences: list of sentences
        :return: list where each element is either the cached embedding or None.
        """
        try:
            keys = [self._get_key_hash(sentence) for sentence in sentences]
            results = []
            with self.redis_client.pipeline() as pipe:
                for key in keys:
                    pipe.get(key)
                results = pipe.execute()
            for result in results:
                if result is not None:
                    results.append(np.frombuffer(result, dtype=self.embedding_dtype))
                else:
                    results.append(None)
            return results
        except Exception as e:
            print(f"Failed to cache sentence: {e}")
            return None

    def cache_sentence(self, sentence : str, embedding : np.ndarray) -> bool:
        """
        cache the sentence and its embedding.
        :param sentence:
        :param embedding:
        :return: True if successful, False otherwise.
        """
        try:
            key = self._get_key_hash(sentence)
            self.redis_client.set(key, embedding.tobytes())
            return True
        except Exception as e:
            print(f"Failed to cache sentence: {e}")
            return False

    def clear_cache(self):
        """
        do not use this function.
        """
        pass
        #self.redis_client.flushdb()