import torch
import torch.nn as nn
from torch.onnx.ops import attention

from model.model.attention import HybridEncoder, global_context_aggregation
from model.model.input_representation import InputRepresentation
from model.model.policy_head import PolicyHead
from model.model.preprocessing import FeaturePreprocessor
from model.model.action_discretization import *
from model.api.schema_validation.state_schema import StatePayload


class DeepSetsWithAttentionModel(nn.Module):
    def __init__(self):
        super().__init__()

        #data params
        self.grid_x = 6
        self.grid_y = 4
        self.max_windows = 20
        self.max_workspace_number = 10

        #model params
        self.model_dtype = torch.float32
        self.batch_size = 32
        self.input_scalar_features_dim = 8
        self.input_text_dim = 384

        self.hidden_scalar_preprocessor_dim = 64
        self.model_scalar_dim = 128
        self.model_text_dim = 128
        self.preprocessor_scalar_dropout_rate = 0.1
        self.preprocessor_text_dropout_rate = 0.1

        self.model_dim = 256
        self.hidden_ff_dim = 512
        self.attention_dropout_rate = 0.1
        self.ff_dropout_rate = 0.1

        self.hidden_action_dim = 256
        self.action_dropout_rate = 0.1

        #sub-modules
        self.input_representation = InputRepresentation(
            grid_x=self.grid_x,
            grid_y=self.grid_y,
            max_windows=self.max_windows,
            max_workspace_number=self.max_workspace_number,
            window_description_embedding_size=self.input_text_dim,
            scalar_features_size=self.input_scalar_features_dim,
            batch_size=self.batch_size
        )

        self.feature_preprocessor = FeaturePreprocessor(
            input_data_dim=self.input_scalar_features_dim,
            hidden_preprocessor_dim=self.hidden_scalar_preprocessor_dim,
            output_model_dim_scalar=self.model_scalar_dim,
            dropout_rate_scalar=self.preprocessor_scalar_dropout_rate,
            input_text_dim=self.input_text_dim,
            output_model_dim_text=self.model_text_dim,
            dropout_rate_text=self.preprocessor_text_dropout_rate
        )

        self.attention = HybridEncoder(
            model_dim=self.model_dim,
            hidden_ff_dim=self.hidden_ff_dim,
            dropout_rate_attention=self.attention_dropout_rate,
            dropout_rate_ff=self.ff_dropout_rate
        )

        self.policy_head = PolicyHead(
            model_dim=self.model_dim,
            hidden_action_dim=self.hidden_action_dim,
            dropout_rate=self.action_dropout_rate
        )

    def count_parameters(self):
        """
        count total trainable parameters in the model
        """
        return sum(p.numel() for p in self.parameters() if p.requires_grad)

    def get_parameter_breakdown(self):
        """
        get detailed breakdown of parameters by module
        """
        breakdown = {}
        for name, module in self.named_children():
            breakdown[name] = sum(p.numel() for p in module.parameters() if p.requires_grad)
        return breakdown

    def init_weights(self):
        pass

    def forward(self, batch : list[StatePayload]):
        if len(batch) <= 0 or len(batch) > self.batch_size:
            raise ValueError("invalid batch size")
        description_embeddings, scalar_features, mask = self.input_representation.process_input(batch)
        preprocessed_features = self.feature_preprocessor.forward(scalar_features, description_embeddings)
        attention_output = self.attention.forward(preprocessed_features, mask)
        global_context = global_context_aggregation(attention_output, mask)
        prob_tlx, prob_tly, prob_brx, prob_bry, prob_ws = self.policy_head.forward(attention_output, global_context)
        #todo

    def save(self):
        pass

    def load(self):
        pass
