import torch
from sentence_transformers import SentenceTransformer
import math

from model.api.schema_validation.state_schema import StatePayload
from model.config import config

class TextEmbedder:
    def __init__(self):
        self.model = SentenceTransformer(model_name_or_path="all-MiniLM-L6-v2")
        self.model.eval()

    def embed_window_description(self, window_descriptions : list[str]) -> torch.Tensor:
        """
        embeds windows descriptions using sentence transformer.
        :param window_descriptions: list of window descriptions
        :return: tensor of shape (batch_size, windows_number, 384)
        """
        with torch.no_grad():
            embeddings = self.model.encode(window_descriptions, convert_to_tensor=True)
        return embeddings


class InputRepresentation:
    def __init__(self, grid_x, grid_y, max_windows, workspace_number):
        #input params
        self.max_batch_size = 32 #todo
        self.max_windows = max_windows
        self.model_input_size = 392
        self.window_description_embedding_size = 384
        self.scalar_features_size = 8

        #normalization params
        self.grid_x_max = grid_x - 1
        self.grid_y_max = grid_y - 1
        self.workspace_number_max = workspace_number - 1
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

        :raises ValueError: If the size of `payloads` exceeds the allowed batch size range.
        """
        if len(payloads) <= 0 or len(payloads) > self.max_batch_size:
            raise ValueError("invalid batch size")
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