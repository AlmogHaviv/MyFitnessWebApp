# train_pipeline.py
import torch
import asyncio
import json
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset as TorchDataset # Renamed to avoid conflict
from sklearn.model_selection import train_test_split # For robust splitting
import os
import time
import random
import numpy as np

# Assuming preprocess.py, dataset.py, model.py are in the same directory or accessible
from preprocess import load_events_from_mongo, encode_ids, build_liked_disliked_pairs
from dataset import InteractionDataset # Your custom dataset
from model import MFModel

# --- Helper Functions ---
def save_model_checkpoint(model, id_to_index, index_to_id, model_dir="matrix_factorization_v2"):
    os.makedirs(model_dir, exist_ok=True)
    
    model_path = os.path.join(model_dir, "mf_model.pt")
    torch.save({
        'model_state_dict': model.state_dict(),
        'model_config': {
            'num_users': model.user_embed.num_embeddings,
            'embedding_dim': model.user_embed.embedding_dim
        }
    }, model_path)
    
    mappings_path = os.path.join(model_dir, "id_mappings.json")
    # Ensure keys in index_to_id are strings for JSON compatibility if they aren't already
    # Typically, index_to_id maps int_index -> original_str_id
    # id_to_index maps original_str_id -> int_index
    with open(mappings_path, "w") as f:
        json.dump({
            'id_to_index': id_to_index, # Should be str_id: int_idx
            'index_to_id': {str(k): v for k, v in index_to_id.items()} # Ensure keys are str for JSON
        }, f)
    
    print(f"Model saved to {model_path}")
    print(f"ID mappings saved to {mappings_path}")

def load_model_checkpoint(model_dir="matrix_factorization_v2"):
    model_path = os.path.join(model_dir, "mf_model.pt")
    if not os.path.exists(model_path):
        print(f"Model checkpoint not found at {model_path}")
        return None, None, None
        
    checkpoint = torch.load(model_path)
    
    model_config = checkpoint['model_config']
    model = MFModel(
        num_users=model_config['num_users'],
        embedding_dim=model_config['embedding_dim']
    )
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval() # Set to evaluation mode
    
    mappings_path = os.path.join(model_dir, "id_mappings.json")
    if not os.path.exists(mappings_path):
        print(f"ID mappings not found at {mappings_path}")
        return model, None, None # Return model even if mappings are missing

    with open(mappings_path, "r") as f:
        mappings = json.load(f)
    
    # Convert index_to_id keys back to integers for internal consistency if needed by other parts of your code
    # However, recommend_partners will use integer indices, and mapping back uses this dict.
    # If you use index_to_id[int_key], then convert:
    # index_to_id = {int(k): v for k, v in mappings['index_to_id'].items()}
    # For now, keep as string keys as loaded, ensure usage is consistent.
    id_to_index = mappings['id_to_index']
    index_to_id = mappings['index_to_id'] # Keys will be strings

    print(f"Model loaded from {model_path}")
    return model, id_to_index, index_to_id


def generate_negative_samples(positive_pairs, all_known_interactions_set, n_users, num_neg_per_positive):
    """
    Generates negative samples for training.
    A negative sample is a (user, item) pair that the user has not interacted with.
    """
    negatives = []
    for u, p_pos in positive_pairs:
        added_negatives = 0
        attempts = 0
        while added_negatives < num_neg_per_positive and attempts < n_users * 2: # Limit attempts
            neg_p = random.randint(0, n_users - 1)
            if u != neg_p and (u, neg_p) not in all_known_interactions_set:
                negatives.append((u, neg_p))
                added_negatives += 1
            attempts += 1
    return negatives

def calculate_precision_at_k(model, user_idx, true_positive_partners_set, all_partner_indices_tensor, k, device):
    """
    Calculates precision@k for a single user.
    true_positive_partners_set: A set of partner indices that are true positives for this user.
    all_partner_indices_tensor: A tensor of all possible partner indices.
    """
    if not true_positive_partners_set:
        return 0.0  # Or handle as 1.0 if no recommendations and no true positives

    model.eval()
    with torch.no_grad():
        user_tensor = torch.LongTensor([user_idx] * len(all_partner_indices_tensor)).to(device)
        scores = model(user_tensor, all_partner_indices_tensor)
        
        # Exclude the user themselves from being recommended
        scores[user_idx] = -float('inf') 

        # Get top K recommendations
        _, top_k_indices = torch.topk(scores, k)
        recommended_partners = set(top_k_indices.cpu().tolist())
    
    hits = len(recommended_partners.intersection(true_positive_partners_set))
    return hits / k if k > 0 else 0.0

# --- Training and Evaluation ---
def train_and_evaluate_model(
    n_users, 
    all_liked_pairs, 
    all_disliked_pairs, 
    id_to_index, 
    index_to_id,
    embedding_dim=32, 
    epochs=20, 
    batch_size=64, 
    lr=0.005, 
    weight_decay=1e-5, # L2 regularization
    k_eval=10,
    num_neg_per_positive=1, # Number of negative samples per positive interaction for training
    val_test_split_ratio=0.1, # 10% for test
    train_val_split_ratio=0.125 # (effectively 10% of original for val, 80% for train: 0.1 / 0.8 = 0.125 of remaining)
):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # 1. Prepare all known interactions (user_idx, partner_idx, label)
    interactions = []
    for u, p in all_liked_pairs:
        interactions.append({'user': u, 'partner': p, 'label': 1.0})
    for u, p in all_disliked_pairs:
        interactions.append({'user': u, 'partner': p, 'label': 0.0})
    
    if not interactions:
        print("No interactions found to train the model.")
        return None, 0.0

    # 2. Split into Train+Validation and Test sets
    # Stratify by user if possible and desired, for simplicity direct split here
    # Ensure 'user' is used for stratification if many users have few interactions
    try:
        train_val_interactions, test_interactions = train_test_split(
            interactions, test_size=val_test_split_ratio, random_state=42, 
            stratify=[inter['user'] for inter in interactions] if len(set(inter['user'] for inter in interactions)) > 1 else None
        )
    except ValueError: # Stratification not possible (e.g. some users only in test set after split)
        train_val_interactions, test_interactions = train_test_split(
            interactions, test_size=val_test_split_ratio, random_state=42
        )


    # 3. Split Train+Validation into Training and Validation sets
    try:
        train_interactions, val_interactions = train_test_split(
            train_val_interactions, test_size=train_val_split_ratio, random_state=42, # 0.125 of (1-0.1) = approx 0.1 of total
            stratify=[inter['user'] for inter in train_val_interactions] if len(set(inter['user'] for inter in train_val_interactions)) > 1 else None
        )
    except ValueError:
         train_interactions, val_interactions = train_test_split(
            train_val_interactions, test_size=train_val_split_ratio, random_state=42
        )


    print(f"Total interactions: {len(interactions)}")
    print(f"Training interactions: {len(train_interactions)}")
    print(f"Validation interactions: {len(val_interactions)}")
    print(f"Test interactions: {len(test_interactions)}")

    # Prepare data for training
    train_positive_pairs = [(item['user'], item['partner']) for item in train_interactions if item['label'] == 1.0]
    train_disliked_explicit = [(item['user'], item['partner']) for item in train_interactions if item['label'] == 0.0]

    all_known_interactions_set = set((item['user'], item['partner']) for item in interactions) # All known pairs
    
    train_negative_samples = generate_negative_samples(train_positive_pairs, all_known_interactions_set, n_users, num_neg_per_positive)

    train_user_ids = [u for u, p in train_positive_pairs] + [u for u,p in train_disliked_explicit] + [u for u,p in train_negative_samples]
    train_partner_ids = [p for u, p in train_positive_pairs] + [p for u,p in train_disliked_explicit] + [p for u,p in train_negative_samples]
    train_labels = [1.0] * len(train_positive_pairs) + [0.0] * len(train_disliked_explicit) + [0.0] * len(train_negative_samples)
    
    if not train_user_ids:
        print("No training data after processing (no positive pairs perhaps). Aborting.")
        return None, 0.0

    train_dataset = InteractionDataset(train_user_ids, train_partner_ids, train_labels)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    # Prepare validation data (for per-user evaluation)
    val_user_to_liked_partners = {}
    for item in val_interactions:
        if item['label'] == 1.0:
            val_user_to_liked_partners.setdefault(item['user'], set()).add(item['partner'])
    
    val_users_with_likes = sorted(list(val_user_to_liked_partners.keys()))

    # Initialize model, optimizer, and loss
    model = MFModel(num_users=n_users, embedding_dim=embedding_dim).to(device)
    optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay) # Added weight_decay
    criterion = nn.BCELoss()

    best_val_precision = -1.0
    best_model_state = None
    
    all_partner_indices_tensor = torch.LongTensor(list(range(n_users))).to(device)

    for epoch in range(epochs):
        model.train()
        epoch_loss = 0.0
        for batch_user_ids, batch_partner_ids, batch_labels in train_loader:
            batch_user_ids = batch_user_ids.to(device)
            batch_partner_ids = batch_partner_ids.to(device)
            batch_labels = batch_labels.to(device)

            optimizer.zero_grad()
            predictions = model(batch_user_ids, batch_partner_ids)
            loss = criterion(predictions, batch_labels)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()
        
        avg_epoch_loss = epoch_loss / len(train_loader) if len(train_loader) > 0 else 0
        print(f"Epoch {epoch + 1}/{epochs} - Training Loss: {avg_epoch_loss:.4f}")

        # Validation phase (per-user precision@k)
        model.eval()
        current_val_precisions = []
        if val_users_with_likes: # Only evaluate if there are users with liked items in validation
            for user_idx in val_users_with_likes:
                true_positives_for_user = val_user_to_liked_partners.get(user_idx, set())
                if true_positives_for_user: # Should always be true due to val_users_with_likes
                    precision = calculate_precision_at_k(model, user_idx, true_positives_for_user, all_partner_indices_tensor, k_eval, device)
                    current_val_precisions.append(precision)
            
            avg_val_precision = np.mean(current_val_precisions) if current_val_precisions else 0.0
            print(f"Epoch {epoch + 1}/{epochs} - Validation Precision@{k_eval}: {avg_val_precision:.4f} (on {len(val_users_with_likes)} users)")

            if avg_val_precision > best_val_precision:
                best_val_precision = avg_val_precision
                best_model_state = model.state_dict().copy()
                print(f"New best validation precision: {best_val_precision:.4f}. Saving model state.")
        else:
            print(f"Epoch {epoch + 1}/{epochs} - No users with likes in validation set. Skipping precision calculation.")
            # If no validation data, consider saving the last model or based on loss
            if best_model_state is None: # Save at least one model state
                 best_model_state = model.state_dict().copy()


    # Load best model state for final testing
    if best_model_state:
        model.load_state_dict(best_model_state)
        print("Loaded best model state for final testing.")
        save_model_checkpoint(model, id_to_index, index_to_id) # Save the best model
    else:
        print("No best model state found (e.g., no validation data or no improvement). Using last model state.")
        save_model_checkpoint(model, id_to_index, index_to_id) # Save the last model

    # Final Test Evaluation
    model.eval()
    test_user_to_liked_partners = {}
    for item in test_interactions:
        if item['label'] == 1.0:
            test_user_to_liked_partners.setdefault(item['user'], set()).add(item['partner'])
    
    test_users_with_likes = sorted(list(test_user_to_liked_partners.keys()))
    final_test_precisions = []

    if test_users_with_likes:
        for user_idx in test_users_with_likes:
            true_positives_for_user = test_user_to_liked_partners.get(user_idx, set())
            if true_positives_for_user:
                precision = calculate_precision_at_k(model, user_idx, true_positives_for_user, all_partner_indices_tensor, k_eval, device)
                final_test_precisions.append(precision)
        
        avg_test_precision = np.mean(final_test_precisions) if final_test_precisions else 0.0
        print(f"--- Final Test Precision@{k_eval}: {avg_test_precision:.4f} (on {len(test_users_with_likes)} users) ---")
    else:
        avg_test_precision = 0.0
        print("--- No users with likes in test set. Final Test Precision@k is 0. ---")
        
    return model, avg_test_precision


def recommend_partners_for_user(model, user_idx_internal, n_users, k_recommend, index_to_id, device=None):
    """
    Recommends k partners for a given user.
    user_idx_internal: The internal integer index of the user.
    index_to_id: Mapping from internal integer index to original string ID.
    """
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    model.to(device) # Ensure model is on the correct device
    model.eval()

    with torch.no_grad():
        user_tensor = torch.LongTensor([user_idx_internal] * n_users).to(device)
        all_partner_indices_tensor = torch.LongTensor(list(range(n_users))).to(device)
        
        scores = model(user_tensor, all_partner_indices_tensor)
        
        # Don't recommend the user to themselves
        scores[user_idx_internal] = -float('inf')
        
        # Potentially filter out items already interacted with by the user (from training data)
        # This requires access to the user's interaction history. For simplicity, not implemented here.

        top_k_scores, top_k_indices = torch.topk(scores, min(k_recommend, n_users))
        
    recommended_internal_indices = top_k_indices.cpu().tolist()
    
    # Map internal indices back to original string IDs
    # Ensure index_to_id keys are strings if that's how they are stored (e.g., after loading from JSON)
    recommended_original_ids = [index_to_id.get(str(idx), f"unknown_id_{idx}") for idx in recommended_internal_indices]
    
    return recommended_original_ids, recommended_internal_indices, top_k_scores.cpu().tolist()


# --- Main Execution ---
async def run_training_pipeline():
    print("Starting training pipeline...")
    events = await load_events_from_mongo()
    if not events:
        print("No events loaded from MongoDB. Exiting.")
        return

    id_to_index, index_to_id = encode_ids(events) # id_to_index: str_id -> int_idx, index_to_id: int_idx -> str_id
    liked_pairs, disliked_pairs = build_liked_disliked_pairs(events, id_to_index)

    n_users = len(id_to_index)
    if n_users == 0:
        print("No users found after encoding IDs. Exiting.")
        return

    print(f"Number of users: {n_users}")
    print(f"Liked pairs: {len(liked_pairs)}, Disliked pairs: {len(disliked_pairs)}")

    # Train the model
    trained_model, final_test_precision = train_and_evaluate_model(
        n_users=n_users,
        all_liked_pairs=liked_pairs,
        all_disliked_pairs=disliked_pairs,
        id_to_index=id_to_index,
        index_to_id=index_to_id, # Pass original index_to_id (int keys)
        embedding_dim=50,      # Hyperparameter
        epochs=25,             # Hyperparameter
        batch_size=128,        # Hyperparameter
        lr=0.001,              # Hyperparameter
        weight_decay=1e-5,     # L2 Regularization
        k_eval=10,
        num_neg_per_positive=2 # Hyperparameter
    )

    if trained_model:
        print(f"\nTraining complete. Final Test Precision@{10}: {final_test_precision:.4f}")

        # Example: Get recommendations for a sample user (if users exist)
        # Ensure id_to_index and index_to_id from the saved model are used if loading,
        # or the ones from the current session if using the currently trained model.
        
        # To use a loaded model instead:
        # loaded_model, loaded_id_to_index, loaded_index_to_id = load_model_checkpoint()
        # if loaded_model:
        #    model_to_use = loaded_model
        #    id_map_for_reco = loaded_index_to_id # Keys are strings here
        #    # ... pick a user ...
        # else:
        #    print("Could not load model for recommendation example.")
        #    return

        model_to_use = trained_model
        id_map_for_reco = {str(k):v for k,v in index_to_id.items()} # Ensure string keys for lookup consistency

        # Find a user's original ID and then their internal index
        sample_original_user_id = None
        if id_to_index: # Check if id_to_index is not empty
            sample_original_user_id = list(id_to_index.keys())[0] # Get the first user's original ID
            user_idx_internal = id_to_index.get(sample_original_user_id)

            if user_idx_internal is not None:
                print(f"\n--- Example Recommendation for original user ID: {sample_original_user_id} (internal index: {user_idx_internal}) ---")
                start_time = time.time()
                
                recommended_ids, internal_indices, scores = recommend_partners_for_user(
                    model=model_to_use, 
                    user_idx_internal=user_idx_internal, 
                    n_users=n_users, 
                    k_recommend=5,
                    index_to_id=id_map_for_reco # Use the str-keyed version
                )
                inference_time = time.time() - start_time
                
                print(f"Inference took {inference_time:.4f} seconds.")
                print(f"Top recommended partner original IDs for user {sample_original_user_id}: {recommended_ids}")
                print(f"Their internal indices: {internal_indices}")
                print(f"Their scores: {[f'{s:.4f}' for s in scores]}")
            else:
                print(f"Could not find internal index for user ID: {sample_original_user_id}")
        else:
            print("No users available to make a sample recommendation.")
    else:
        print("Model training failed.")

if __name__ == "__main__":
    # If your preprocess.py also has an asyncio.run(main()), 
    # ensure they don't conflict or call populate_events if needed.
    # For this script, we assume events are already populated or populate_events is run separately.
    # Example:
    # from preprocess import populate_events
    # asyncio.run(populate_events()) # Run this first if you need to generate data

    asyncio.run(run_training_pipeline())