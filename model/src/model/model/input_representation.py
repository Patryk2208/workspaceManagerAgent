import torch
import numpy as np
from sentence_transformers import SentenceTransformer
import math

from torch.nn.functional import embedding

from model.api.schema_validation.state_schema import StatePayload
from model.model.embedding_caching import EmbeddingCaching


class TextEmbedder:
    def __init__(self):
        self.cache = EmbeddingCaching()
        self.model = SentenceTransformer(model_name_or_path="all-MiniLM-L6-v2")
        self.model.eval()

    def embed_window_description(self, window_descriptions : list[str]) -> torch.Tensor:
        """
        embeds windows descriptions using sentence transformer, tries to get a cached embedding, if not present,
        runs the model.
        :param window_descriptions: list of window descriptions
        :return: tensor of shape (batch_size, windows_number, 384)
        """
        embeddings = self.cache.try_get_cache_hit_batch(window_descriptions)
        cache_misses = []
        cache_miss_indices = []
        i = 0
        for e in embeddings:
            if e is None:
                cache_misses.append(e)
                cache_miss_indices.append(i)
            i += 1
        with torch.no_grad():
            new_embeddings = self.model.encode(cache_misses)
        for i in range(len(cache_misses)):
            self.cache.cache_sentence(cache_misses[i], new_embeddings[i])
            embeddings[cache_miss_indices[i]] = new_embeddings[i]
        return torch.tensor(np.stack(embeddings))


class InputRepresentation:
    def __init__(self, grid_x : int, grid_y : int, max_windows : int, max_workspace_number : int,
                 window_description_embedding_size : int, scalar_features_size : int, batch_size : int):
        #input params
        self.batch_size = batch_size
        self.max_windows = max_windows
        self.model_input_size = window_description_embedding_size + scalar_features_size
        self.window_description_embedding_size = window_description_embedding_size
        self.scalar_features_size = scalar_features_size

        #normalization params
        self.grid_x_max = grid_x - 1
        self.grid_y_max = grid_y - 1
        self.workspace_number_max = max_workspace_number - 1
        self.log_duration_max: float = 15

        #text model
        self.text_embedder = TextEmbedder()


    def process_input(self, payloads : list[StatePayload]) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Processes a list of payloads representing window states and transforms them into an
        embedded tensor representation. This function generates embeddings for window
        descriptions and scalar features, handling multiple payloads and aggregating the
        results into a tensor suitable for further processing.

        :param payloads: List of StatePayload objects

        :return: tensors of scalar features and text features, as well as a mask indicating which windows are used.
        Tensor shapes: (batch_size, windows_number, 8), (batch_size, windows_number, 384), (batch_size, windows_number)
        """
        window_descriptions = []
        window_embeddings = torch.zeros(len(payloads), self.max_windows, self.window_description_embedding_size)
        scalar_features = torch.zeros(len(payloads), self.max_windows, self.scalar_features_size)
        mask = torch.zeros(len(payloads), self.max_windows)
        i = 0
        for statePayload in payloads:
            j = 0
            for state in statePayload.window_states:
                window_descriptions.append(state.title)
                scalar_features[i, j, 0] = state.position.tlx / self.grid_x_max
                scalar_features[i, j, 1] = state.position.tly / self.grid_y_max
                scalar_features[i, j, 2] = state.position.brx / self.grid_x_max
                scalar_features[i, j, 3] = state.position.bry / self.grid_y_max
                scalar_features[i, j, 4] = state.workspace_number / self.workspace_number_max
                scalar_features[i, j, 5] = float(state.window_activity.is_focused)
                scalar_features[i, j, 6] = math.log(state.window_activity.current_focus_duration.total_seconds())
                scalar_features[i, j, 7] = math.log(state.window_activity.total_focus_duration.total_seconds())
                mask[i, j] = 1
                j += 1
            window_embeddings[i] = self.text_embedder.embed_window_description(window_descriptions)
            i += 1
        return window_embeddings, scalar_features, mask