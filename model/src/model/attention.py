import torch
import torch.nn as nn
import torch.nn.functional as F

class AttentionLayer(nn.Module):
    def __init__(self, model_dim : int, dropout_rate : float):
        """
        attention layer for better understanding of the relations between windows
        :param model_dim: model dimension
        :param dropout_rate:
        """
        super().__init__()
        self.input_model_dim = model_dim
        self.dropout_rate = dropout_rate

        self.w_q = nn.Linear(model_dim, model_dim)
        self.w_k = nn.Linear(model_dim, model_dim)
        self.w_v = nn.Linear(model_dim, model_dim)
        self.dropout = nn.Dropout(dropout_rate)

    def forward(self, x : torch.Tensor, mask : torch.Tensor) -> torch.Tensor:
        """
        forward pass of the attention layer
        :param x: preprocessed input representation tensor of shape (batch_size, windows_number, input_model_dim)
        :param mask: mask tensor of shape (batch_size, windows_number) indicating which windows are just padding
        :return: result of self-attention, tensor of shape (batch_size, windows_number, input_model_dim)
        """
        batch_size, windows_number, input_model_dim = x.shape
        # Q, K, V attention projections
        Q = self.w_q(x)
        K = self.w_k(x)
        V = self.w_v(x)
        # calculating attention scores
        scores = torch.matmul(Q, K.transpose(-2, -1)) / torch.sqrt(torch.tensor(self.input_model_dim, dtype=torch.float32))
        #masking for padded input
        key_mask = mask.unsqueeze(1).expand(batch_size, windows_number, windows_number)
        scores = scores.masked_fill(~key_mask, float('-inf'))
        #softmax and dropout
        weights = F.softmax(scores, dim=-1)
        weights = self.dropout(weights)
        #weighted sum
        output = torch.matmul(weights, V)
        #residual connection
        output = output + x
        return output


class FeedForwardLayer(nn.Module):
    def __init__(self, model_dim : int, hidden_ff_dim : int, dropout_rate : float):
        """
        feed-forward layer for better understanding of the relations between windows post-attention
        :param model_dim: model dimension
        :param hidden_ff_dim: hidden dimension of the feed-forward layer
        :param dropout_rate:
        """
        super().__init__()
        self.hidden_ff_dim = hidden_ff_dim or 4 * model_dim
        self.ff = nn.Sequential(
            nn.Linear(model_dim, self.hidden_ff_dim),
            nn.GELU(),
            nn.Dropout(dropout_rate),
            nn.Linear(self.hidden_ff_dim, model_dim),
            nn.Dropout(dropout_rate)
        )

        self.layer_norm = nn.LayerNorm(model_dim)

    def forward(self, x : torch.Tensor) -> torch.Tensor:
        """
        feed-forward layer forward pass and layer normalization
        :param x: output of the attention layer, tensor of shape (batch_size, windows_number, input_model_dim)
        :return: result of the feed-forward layer, tensor of shape (batch_size, windows_number, input_model_dim)
        """
        x += self.ff(x)
        x = self.layer_norm(x)
        return x

class HybridEncoder(nn.Module):
    def __init__(self, model_dim : int, hidden_ff_dim : int,
                 dropout_rate_attention : float, dropout_rate_ff : float):
        """
        this module combines attention and feed-forward layers
        :param model_dim: model dimension
        :param hidden_ff_dim:
        :param dropout_rate_attention:
        :param dropout_rate_ff:
        """
        super().__init__()
        self.attention = AttentionLayer(model_dim, dropout_rate_attention)
        self.feed_forward = FeedForwardLayer(model_dim, hidden_ff_dim, dropout_rate_ff)
        self.layer_norm = nn.LayerNorm(model_dim)

    def forward(self, x : torch.Tensor, mask : torch.Tensor) -> torch.Tensor:
        """
        combined forward pass of the attention and feed-forward layers
        :param x: preprocessed input representation tensor of shape (batch_size, windows_number, input_model_dim)
        :param mask: mask tensor of shape (batch_size, windows_number) indicating which windows are just padding
        :return: post attention and feed-forward result, tensor of shape (batch_size, windows_number, input_model_dim)
        """
        x = self.attention.forward(x, mask)
        x = self.layer_norm(x)
        x = self.feed_forward.forward(x)
        return x

def global_context_aggregation(x : torch.Tensor, mask : torch.Tensor) -> torch.Tensor:
    """
    aggregation function for the global context, sums all the valid features post hybrid encoding
    :param x: data post hybrid encoding, tensor of shape (batch_size, windows_number, input_model_dim)
    :param mask: mask tensor of shape (batch_size, windows_number) indicating which windows are just padding
    :return: aggregated context, tensor of shape (batch_size, input_model_dim)
    """
    masked_features = x * mask.unsqueeze(-1)
    summed_features = torch.sum(masked_features, dim=1)
    num_valid = torch.sum(mask, dim=1, keepdim=True)
    num_valid = num_valid.clamp(min=1e-6)
    return summed_features / num_valid