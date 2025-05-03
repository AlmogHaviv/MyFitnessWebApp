import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.model_selection import train_test_split

class SVDPreprocessor:
    def __init__(self, events):
        self.df = pd.DataFrame(events)
        self.action_mapping = {"like": 1, "dislike": -1}

    def build_interaction_matrix(self):
        self.df["interaction"] = self.df["action"].map(self.action_mapping)
        interaction_matrix = self.df.pivot_table(index="user_id", columns="buddy_id", values="interaction", fill_value=0)
        sparse_matrix = csr_matrix(interaction_matrix.values)
        return sparse_matrix, interaction_matrix.index, interaction_matrix.columns

    def split_train_validation(self, test_size=0.2):
        train_df, val_df = train_test_split(self.df, test_size=test_size, stratify=self.df["user_id"], random_state=42)
        return train_df, val_df
