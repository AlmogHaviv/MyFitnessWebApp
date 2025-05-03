# model.py
import torch
import torch.nn as nn

class MFModel(nn.Module):
    def __init__(self, num_users, embedding_dim):
        super(MFModel, self).__init__()
        self.user_embed = nn.Embedding(num_users, embedding_dim)
        self.partner_embed = nn.Embedding(num_users, embedding_dim)

        # Optional: initialization for better convergence
        nn.init.normal_(self.user_embed.weight, std=0.1)
        nn.init.normal_(self.partner_embed.weight, std=0.1)

    def forward(self, user_ids, partner_ids):
        user_vecs = self.user_embed(user_ids)
        partner_vecs = self.partner_embed(partner_ids)
        scores = (user_vecs * partner_vecs).sum(dim=1)
        return torch.sigmoid(scores)
