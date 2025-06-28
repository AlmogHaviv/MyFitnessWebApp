import numpy as np
from sklearn.decomposition import TruncatedSVD
import joblib
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)
from sklearn.preprocessing import MinMaxScaler

def ndcg_at_k_per_user(val_df, recommender, k):
    user_groups = val_df.groupby("user_id")
    ndcgs = []
    for user_id, group in user_groups:
        if user_id not in recommender.user_index:
            continue
        true_labels = []
        pred_scores = []
        for _, row in group.iterrows():
            if row["buddy_id"] in recommender.buddy_index:
                true_labels.append(1 if row["action"] == "like" else 0)
                pred_scores.append(recommender.predict(user_id, row["buddy_id"]))
        if len(true_labels) >= k:
            y_true = np.array(true_labels)
            y_scores = MinMaxScaler().fit_transform(np.array(pred_scores).reshape(-1, 1)).flatten()
            order = np.argsort(y_scores)[::-1]
            y_true_at_k = y_true[order[:k]]
            ideal_sorted = np.sort(y_true_at_k)[::-1]
            dcg = np.sum((2 ** y_true_at_k - 1) / np.log2(np.arange(2, 2 + len(y_true_at_k))))
            ideal = np.sum((2 ** ideal_sorted - 1) / np.log2(np.arange(2, 2 + len(ideal_sorted))))
            if ideal > 0:
                ndcgs.append(dcg / ideal)
    return np.mean(ndcgs) if ndcgs else 0.0



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

        y_true = np.array(y_true)
        y_pred = np.array(y_pred)

        # Normalize predictions to [0, 1]
        scaler = MinMaxScaler()
        y_pred_scaled = scaler.fit_transform(y_pred.reshape(-1, 1)).flatten()

        # Threshold for binary prediction (you can tune this)
        y_pred_binary = (y_pred_scaled >= 0.5).astype(int)

        # Calculate metrics
        mse = np.mean((y_true - y_pred_scaled) ** 2)
        acc = accuracy_score(y_true, y_pred_binary)
        precision = precision_score(y_true, y_pred_binary)
        recall = recall_score(y_true, y_pred_binary)
        f1 = f1_score(y_true, y_pred_binary)
        roc_auc = roc_auc_score(y_true, y_pred_scaled)
        ndcg_6 = ndcg_at_k_per_user(val_df, self, 6)
        ndcg_10 = ndcg_at_k_per_user(val_df, self, 10)


        return {
            "mse": round(mse, 4),
            "accuracy": round(acc, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(roc_auc, 4),
            "ndcg@6": round(ndcg_6, 4),
            "ndcg@10": round(ndcg_10, 4)
        }

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
