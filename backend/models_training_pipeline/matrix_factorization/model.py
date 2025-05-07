# model.py
import torch
import torch.nn as nn

class MFModel(nn.Module):
    def __init__(self, num_users, embedding_dim):
        super(MFModel, self).__init__()
        self.user_embed = nn.Embedding(num_users, embedding_dim)
        self.partner_embed = nn.Embedding(num_users, embedding_dim) # Assuming partners are also users

        self.user_bias = nn.Embedding(num_users, 1)
        self.partner_bias = nn.Embedding(num_users, 1)

        # Initialize weights
        nn.init.normal_(self.user_embed.weight, std=0.1)
        nn.init.normal_(self.partner_embed.weight, std=0.1)
        nn.init.zeros_(self.user_bias.weight)
        nn.init.zeros_(self.partner_bias.weight)

    def forward(self, user_ids, partner_ids):
        user_vecs = self.user_embed(user_ids)
        partner_vecs = self.partner_embed(partner_ids)
        
        dot = (user_vecs * partner_vecs).sum(dim=1)
        
        user_b = self.user_bias(user_ids).squeeze(dim=-1) # Ensure correct squeezing
        partner_b = self.partner_bias(partner_ids).squeeze(dim=-1) # Ensure correct squeezing
        
        return torch.sigmoid(dot + user_b + partner_b)