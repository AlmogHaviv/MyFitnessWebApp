import numpy as np
from sklearn.decomposition import TruncatedSVD
import joblib

class SVDRecommender:
    def __init__(self, n_components=20):
        self.n_components = n_components
        self.model = TruncatedSVD(n_components=self.n_components, random_state=42)
        self.user_factors = None
        self.buddy_factors = None
        self.user_index = None
        self.buddy_index = None

    def train(self, sparse_matrix, user_index, buddy_index):
        self.user_factors = self.model.fit_transform(sparse_matrix)
        self.buddy_factors = self.model.components_.T
        self.user_index = user_index
        self.buddy_index = buddy_index

    def predict(self, user_id, buddy_id):
        u_idx = self.user_index.get_loc(user_id)
        b_idx = self.buddy_index.get_loc(buddy_id)
        return np.dot(self.user_factors[u_idx], self.buddy_factors[b_idx])

    def recommend(self, user_id, top_n=20):
        if user_id not in self.user_index:
            return None
        u_idx = self.user_index.get_loc(user_id)
        scores = np.dot(self.user_factors[u_idx], self.buddy_factors.T)
        top_indices = np.argsort(scores)[::-1][:top_n]
        return self.buddy_index[top_indices]

    def evaluate(self, val_df):
        y_true = []
        y_pred = []
        for _, row in val_df.iterrows():
            if row["user_id"] in self.user_index and row["buddy_id"] in self.buddy_index:
                pred = self.predict(row["user_id"], row["buddy_id"])
                y_pred.append(pred)
                y_true.append(1 if row["action"] == "like" else 0)
        mse = np.mean((np.array(y_true) - np.array(y_pred))**2)
        return mse

    def save(self, path="svd_model"):
        joblib.dump({
            "model": self.model,
            "user_factors": self.user_factors,
            "buddy_factors": self.buddy_factors,
            "user_index": self.user_index,
            "buddy_index": self.buddy_index
        }, f"{path}.joblib")

    def load(self, path="svd_model"):
        data = joblib.load(f"{path}.joblib")
        self.model = data["model"]
        self.user_factors = data["user_factors"]
        self.buddy_factors = data["buddy_factors"]
        self.user_index = data["user_index"]
        self.buddy_index = data["buddy_index"]
