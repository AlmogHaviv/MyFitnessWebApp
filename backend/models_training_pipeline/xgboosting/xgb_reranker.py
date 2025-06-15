from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import make_scorer
from sklearn.metrics import roc_auc_score, accuracy_score, precision_score, recall_score, f1_score, ndcg_score
import pandas as pd
import numpy as np
import xgboost as xgb

def ndcg_at_k_score(y_true, y_score, k=10):
        """
        Custom NDCG@k scorer for binary labels.
        Assumes y_true and y_score are 1D arrays for one user.
        To use in cross-validation, we reshape them into 2D arrays.
        """
        # Reshape as [n_samples, 1] to mimic one user per CV fold
        return ndcg_score(y_true=np.array([y_true]), y_score=np.array([y_score]), k=k)


class XGBReranker:
    def __init__(self):
        self.best_params = {
            'objective': 'binary:logistic',
            'eval_metric': 'auc',
            'use_label_encoder': False,
            'verbosity': 1,
            'subsample': 0.6,
            'scale_pos_weight': 2,
            'n_estimators': 200,
            'min_child_weight': 1,
            'max_depth': 10,
            'learning_rate': 0.01,
            'gamma': 1,
            'colsample_bytree': 0.8
        }
        self.model = xgb.XGBClassifier(**self.best_params)

    def train(self, X_train, y_train, X_val=None, y_val=None):
        if X_val is not None and y_val is not None:
            self.model.fit(
                X_train, y_train,
                eval_set=[(X_val, y_val)],
                verbose=True
            )
        else:
            self.model.fit(X_train, y_train, verbose=True)

    def tune_hyperparameters(self, X_train, y_train, n_iter=30, cv=3):
        param_dist = {
            "n_estimators": [100, 200, 300, 500],
            "max_depth": [3, 5, 7, 10],
            "learning_rate": [0.01, 0.05, 0.1, 0.2],
            "subsample": [0.6, 0.8, 1.0],
            "colsample_bytree": [0.6, 0.8, 1.0],
            "min_child_weight": [1, 3, 5, 7],
            "gamma": [0, 1, 3, 5],
            "scale_pos_weight": [1, 2, 5]  # useful if labels are imbalanced
        }

        scoring = make_scorer(ndcg_at_k_score, needs_proba=True, k=10)
        search = RandomizedSearchCV(
            estimator=xgb.XGBClassifier(objective='binary:logistic', use_label_encoder=False, eval_metric='logloss'),
            param_distributions=param_dist,
            n_iter=n_iter,
            scoring=scoring,
            cv=cv,
            verbose=2,
            random_state=42,
            n_jobs=-1
        )

        print("🔍 Starting hyperparameter search...")
        search.fit(X_train, y_train)
        print("✅ Best parameters found:", search.best_params_)

        # Update model with best found
        self.model = search.best_estimator_

    def predict_proba(self, X):
        return self.model.predict_proba(X)[:, 1]

    def predict(self, X):
        return self.model.predict(X)

    def evaluate(self, X, y_true, user_ids=None):
        y_pred = self.predict(X)
        y_prob = self.predict_proba(X)

        metrics = {
            "accuracy": accuracy_score(y_true, y_pred),
            "precision": precision_score(y_true, y_pred),
            "recall": recall_score(y_true, y_pred),
            "f1_score": f1_score(y_true, y_pred),
            "roc_auc": roc_auc_score(y_true, y_prob)
        }

        # Optional: compute NDCG@6 and NDCG@10 if user_ids are provided
        if user_ids is not None:
            df = pd.DataFrame({
                "user_id": user_ids,
                "y_true": y_true,
                "y_score": y_prob
            })

            def mean_ndcg_at_k(k):
                ndcg_vals = []
                for _, group in df.groupby("user_id"):
                    if group["y_true"].sum() == 0:
                        continue  # skip users with no positives
                    true_relevance = np.expand_dims(group["y_true"].values, axis=0)
                    scores = np.expand_dims(group["y_score"].values, axis=0)
                    ndcg = ndcg_score(true_relevance, scores, k=k)
                    ndcg_vals.append(ndcg)
                return np.mean(ndcg_vals) if ndcg_vals else 0.0

            metrics["ndcg@6"] = mean_ndcg_at_k(6)
            metrics["ndcg@10"] = mean_ndcg_at_k(10)

        return metrics

    def rank(self, X, user_ids, buddy_ids):
        scores = self.predict_proba(X)
        df = pd.DataFrame({
            "user_id": user_ids,
            "buddy_id": buddy_ids,
            "score": scores
        })
        ranked = df.sort_values(by=["user_id", "score"], ascending=[True, False])
        return ranked

    def save(self, path):
        self.model.save_model(path)

    def load(self, path):
        self.model.load_model(path)
