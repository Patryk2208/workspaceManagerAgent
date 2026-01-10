import torch
import torch.nn as nn

class ContextFusion(nn.Module):
    def __init__(self, model_dim : int):
        """
        context fusion layer that combines the attended window representation with the global context.
        :param model_dim: model dimension
        """
        super().__init__()
        self.fuse = nn.Linear(2 * model_dim, model_dim)
        self.layer_norm = nn.LayerNorm(model_dim)

    def forward(self, attended_window_representation : torch.Tensor, global_context : torch.Tensor) -> torch.Tensor:
        """
        forward pass of the context fusion layer
        :param attended_window_representation: output of the attention layer,
        tensor of shape (batch_size, windows_number, model_dim)
        :param global_context: global context tensor of shape (batch_size, model_dim)
        :return: combined representation tensor of shape (batch_size, windows_number, model_dim)
        """
        global_context_expanded = global_context.unsqueeze(1).expand_as(attended_window_representation)
        fused_representation = torch.cat((attended_window_representation, global_context_expanded), dim=-1)
        fused_representation = self.fuse(fused_representation)
        fused_representation = self.layer_norm(fused_representation)
        return fused_representation


class ActionSpaceGenerator(nn.Module):
    def __init__(self, model_dim : int, hidden_action_dim : int, action_space_dim : int, dropout_rate : float):
        """
        last layer of the model that transforms fused features into action space
        :param model_dim: model dimension
        :param hidden_action_dim: hidden dimension of the action space generator
        :param action_space_dim: action space dimension
        :param dropout_rate:
        """
        super().__init__()
        self.mlp = nn.Sequential(
            nn.Linear(model_dim, hidden_action_dim),
            nn.GELU(),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_action_dim, action_space_dim)
        )

    def forward(self, x : torch.Tensor) -> torch.Tensor:
        """
        forward pass of the action space generator
        :param x: input tensor of shape (batch_size, max_windows, model_dim)
        :return: action space tensor of shape (batch_size, max_windows, action_space_dim)
        """
        return self.mlp(x)


class PolicyHead(nn.Module):
    def __init__(self, model_dim : int, hidden_action_dim : int, dropout_rate : float):
        """
        combines the context fusion and action space generator layers into a single policy head class
        :param model_dim: model dimension
        :param hidden_action_dim: hidden dimension of the action space generator
        :param dropout_rate:
        """
        super().__init__()
        self.action_space_dim = 30
        self.top_left_x_max_index = 6
        self.top_left_y_max_index = 10
        self.bottom_right_x_max_index = 16
        self.bottom_right_y_max_index = 20
        self.workspace_number_max_index = 30
        self.context_fusion = ContextFusion(model_dim)
        self.action_space = ActionSpaceGenerator(model_dim, hidden_action_dim, self.action_space_dim, dropout_rate)

    def forward(self, x : torch.Tensor, global_context : torch.Tensor) -> (
            tuple)[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        forward pass of the policy head
        :param x: output of the attention layer
        :param global_context: aggregated global context
        :return: probabilities of the action space
        """
        fused_features = self.context_fusion.forward(x, global_context)
        action_space = self.action_space.forward(fused_features)

        logits_tlx = action_space[..., :self.top_left_x_max_index]
        logits_tly = action_space[..., self.top_left_x_max_index:self.top_left_y_max_index]
        logits_brx = action_space[..., self.top_left_y_max_index:self.bottom_right_x_max_index]
        logits_bry = action_space[..., self.bottom_right_x_max_index:self.bottom_right_y_max_index]
        logits_ws = action_space[..., self.bottom_right_y_max_index:]

        probabilities_tlx = torch.softmax(logits_tlx, dim=-1)
        probabilities_tly = torch.softmax(logits_tly, dim=-1)
        probabilities_brx = torch.softmax(logits_brx, dim=-1)
        probabilities_bry = torch.softmax(logits_bry, dim=-1)
        probabilities_ws = torch.softmax(logits_ws, dim=-1)

        return probabilities_tlx, probabilities_tly, probabilities_brx, probabilities_bry, probabilities_ws

