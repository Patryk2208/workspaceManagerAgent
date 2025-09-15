import torch
import torch.nn as nn

class ScalarFeaturePreprocessor(nn.Module):
    def __init__(self, input_data_dim, hidden_preprocessor_dim, output_model_dim, dropout_rate):
        """
        preprocessing layer for scalar features
        :param input_data_dim: number of scalar features
        :param hidden_preprocessor_dim: hidden layer dimension
        :param output_model_dim: dimension with refined understanding of features for the model
        :param dropout_rate:
        """
        super().__init__()

        self.mlp = nn.Sequential(
            nn.Linear(input_data_dim, hidden_preprocessor_dim),
            nn.LayerNorm(hidden_preprocessor_dim),
            nn.GELU(),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_preprocessor_dim, output_model_dim),
            nn.LayerNorm(output_model_dim),
            nn.GELU(),
            nn.Dropout(dropout_rate)
        )

    def forward(self, scalar_features : torch.Tensor) -> torch.Tensor:
        """
        forward pass of the scalar preprocessing layer
        :param scalar_features: input tensor of shape (batch_size, windows_number, input_data_dim)
        :return: processed tensor of shape (batch_size, windows_number, output_model_dim)
        """
        return self.mlp(scalar_features)


class TextFeaturePreprocessor(nn.Module):
    def __init__(self, input_text_dim, output_model_dim, dropout_rate):
        """
        preprocessing layer for text features
        :param input_text_dim: number of text dimensions
        :param output_model_dim: dimension with refined understanding of text for the model
        :param dropout_rate:
        """
        super().__init__()

        self.projection = nn.Sequential(
            nn.Linear(input_text_dim, output_model_dim),
            nn.LayerNorm(output_model_dim),
            nn.GELU(),
            nn.Dropout(dropout_rate)
        )

    def forward(self, text_embeddings : torch.Tensor) -> torch.Tensor:
        """
        forward pass of the text preprocessing layer
        :param text_embeddings: input tensor of shape (batch_size, windows_number, input_text_dim)
        :return: processed tensor of shape (batch_size, windows_number, output_model_dim)
        """
        return self.projection(text_embeddings)


class FeaturePreprocessor(nn.Module):
    def __init__(self, input_data_dim, hidden_preprocessor_dim, output_model_dim, dropout_rate_scalar,
                 input_text_dim, output_model_dim_text, dropout_rate_text):
        """
        collective preprocessing layer for both scalar and text features
        """
        super().__init__()
        self.scalar_preprocessor = ScalarFeaturePreprocessor(input_data_dim, hidden_preprocessor_dim, output_model_dim, dropout_rate_scalar)
        self.text_preprocessor = TextFeaturePreprocessor(input_text_dim, output_model_dim_text, dropout_rate_text)

    def forward(self, scalar_features : torch.Tensor, text_embeddings : torch.Tensor) -> torch.Tensor:
        """
        processes the input features into model dimensions
        :param scalar_features: input scalar features tensor of shape (batch_size, windows_number, input_data_dim)
        :param text_embeddings: input text embeddings tensor of shape (batch_size, windows_number, input_text_dim)
        :return: model-ready features tensor of shape
        (batch_size, windows_number, output_model_dim_scalar + output_model_dim_text)
        """
        processed_scalar_features = self.scalar_preprocessor(scalar_features)
        processed_text_embeddings = self.text_preprocessor(text_embeddings)
        return torch.cat((processed_scalar_features, processed_text_embeddings), dim=-1)
