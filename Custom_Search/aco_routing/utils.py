import random
from typing import Dict

def compute_edge_desirability(
    pheromone_value: float, 
    edge_cost: float, 
    alpha: float, 
    beta: float
) -> float:
    """Compute the desirability of an edge based on pheromones and cost
    
    Args:
        pheromone_value: The amount of pheromone on the edge
        edge_cost: The cost of traversing the edge
        alpha: Pheromone importance factor
        beta: Distance importance factor
        
    Returns:
        float: The desirability value of the edge
    """
    # Avoid division by zero
    if edge_cost == 0:
        edge_cost = 1e-10
        
    # Formula: τᵢⱼᵅ * (1/dᵢⱼ)ᵝ
    return (pheromone_value ** alpha) * ((1 / edge_cost) ** beta)

def roulette_wheel_selection(probabilities: Dict[str, float]) -> str:
    """Select a key from a dictionary based on probability values
    
    Args:
        probabilities: Dict mapping items to their probabilities
        
    Returns:
        The selected key
    """
    # Guard against empty dictionary
    if not probabilities:
        return None
        
    # Handle the case where there's only one option
    if len(probabilities) == 1:
        return list(probabilities.keys())[0]
    
    # Ensure probabilities sum to 1
    total = sum(probabilities.values())
    normalized_probs = {k: v/total for k, v in probabilities.items()}
    
    # Pick a random point on the probability line
    r = random.random()
    
    # Find the item that corresponds to this point
    cumulative = 0
    for item, prob in normalized_probs.items():
        cumulative += prob
        if r <= cumulative:
            return item
            
    # Fallback: return random item (should rarely happen)
    return random.choice(list(probabilities.keys()))