# dataset.py
import torch
from torch.utils.data import Dataset

class InteractionDataset(Dataset):
    def __init__(self, user_ids, partner_ids, labels):
        self.user_ids = torch.LongTensor(user_ids)
        self.partner_ids = torch.LongTensor(partner_ids)
        self.labels = torch.FloatTensor(labels)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return self.user_ids[idx], self.partner_ids[idx], self.labels[idx]
