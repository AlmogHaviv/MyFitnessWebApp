import torch
import asyncio
import json
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from preprocess import load_events_from_mongo, encode_ids, build_liked_disliked_pairs
import os
import time

from dataset import InteractionDataset
from model import MFModel

import random

def generate_negative_samples(n_users, liked_pairs, num_neg=1):
    all_users = set(range(n_users))
    liked_set = set(liked_pairs)
    negatives = []
    for u, _ in liked_pairs:
        while len(negatives) < num_neg * len(liked_pairs):
            neg = random.randint(0, n_users - 1)
            if (u, neg) not in liked_set and u != neg:
                negatives.append((u, neg))
    return negatives

def save_model(model, id_to_index, index_to_id, model_dir="matrix_factorization"):
    """
    Save the trained model and ID mappings
    """
    # Create directory if it doesn't exist
    os.makedirs(model_dir, exist_ok=True)
    
    # Save model state
    model_path = os.path.join(model_dir, "mf_model.pt")
    torch.save({
        'model_state_dict': model.state_dict(),
        'model_config': {
            'num_users': model.user_embed.num_embeddings,
            'embedding_dim': model.user_embed.embedding_dim
        }
    }, model_path)
    
    # Save ID mappings
    mappings_path = os.path.join(model_dir, "id_mappings.json")
    with open(mappings_path, "w") as f:
        json.dump({
            'id_to_index': id_to_index,
            'index_to_id': index_to_id
        }, f)
    
    print(f"Model saved to {model_path}")
    print(f"ID mappings saved to {mappings_path}")

def load_model(model_dir="matrix_factorization"):
    """
    Load the trained model and ID mappings
    """
    # Load model state
    model_path = os.path.join(model_dir, "mf_model.pt")
    checkpoint = torch.load(model_path)
    
    # Create model with saved configuration
    model = MFModel(
        num_users=checkpoint['model_config']['num_users'],
        embedding_dim=checkpoint['model_config']['embedding_dim']
    )
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()  # Set to evaluation mode
    
    # Load ID mappings
    mappings_path = os.path.join(model_dir, "id_mappings.json")
    with open(mappings_path, "r") as f:
        mappings = json.load(f)
    
    return model, mappings['id_to_index'], mappings['index_to_id']

def train_model(n_users, liked_pairs, disliked_pairs, embedding_dim=32, epochs=10, batch_size=64, lr=0.01):
    # Prepare data
    negatives = generate_negative_samples(n_users, liked_pairs)
    
    # Combine liked, disliked and negative samples
    user_ids = [u for u, p in liked_pairs] + [u for u, p in disliked_pairs] + [u for u, p in negatives]
    partner_ids = [p for u, p in liked_pairs] + [p for u, p in disliked_pairs] + [p for u, p in negatives]
    labels = [1] * len(liked_pairs) + [0] * len(disliked_pairs) + [0] * len(negatives)

    dataset = InteractionDataset(user_ids, partner_ids, labels)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    # Initialize model
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = MFModel(num_users=n_users, embedding_dim=embedding_dim).to(device)
    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = nn.BCELoss()

    # Train loop
    for epoch in range(epochs):
        model.train()
        total_loss = 0.0
        for user_ids, partner_ids, labels in dataloader:
            user_ids, partner_ids, labels = user_ids.to(device), partner_ids.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(user_ids, partner_ids)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        
        print(f"Epoch {epoch + 1}: Loss = {total_loss:.4f}")

    return model

def recommend_partners(model, user_id, n_users, top_k=10):
    model.eval()
    with torch.no_grad():
        user_tensor = torch.LongTensor([user_id] * n_users)
        partner_tensor = torch.LongTensor(list(range(n_users)))
        scores = model(user_tensor, partner_tensor)
        top_k_ids = torch.topk(scores, top_k).indices.tolist()
        return top_k_ids

# Example usage:
if __name__ == "__main__":
    async def main():
        events = await load_events_from_mongo()  # Await the async function
        id_to_index, index_to_id = encode_ids(events)
        liked_pairs, disliked_pairs = build_liked_disliked_pairs(events, id_to_index)

        n_users = len(id_to_index)
        model = train_model(n_users, liked_pairs, disliked_pairs)
        
        # Save the trained model and ID mappings
        save_model(model, id_to_index, index_to_id)
            
        user_id = 0
        start_time = time.time()
        recommended_ids = recommend_partners(model, user_id, n_users)
        inference_time = time.time() - start_time
        print(f"Inference took {inference_time:.4f} seconds")
        print(f"Top matches for user {user_id}: {recommended_ids}")
        print(f"Corresponding real IDs: {[index_to_id[rid] for rid in recommended_ids]}")

    # Run the async main function
    asyncio.run(main())