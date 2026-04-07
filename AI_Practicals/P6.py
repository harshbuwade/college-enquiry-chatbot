import math
def alpha_beta(current_depth, node_index, is_max_player, leaf_values, alpha, beta):
    if current_depth == 3:
        return leaf_values[node_index]
    if is_max_player:
        best_value = -math.inf  
        for i in range(2):
            value = alpha_beta(current_depth + 1,
                               node_index * 2 + i,
                               False,
                               leaf_values,
                               alpha,
                               beta)
            best_value = max(best_value, value)
            alpha = max(alpha, best_value)
            if beta <= alpha:
                break
        return best_value
    else:
        best_value = math.inf  
        for i in range(2):
            value = alpha_beta(current_depth + 1,
                               node_index * 2 + i,
                               True,
                               leaf_values,
                               alpha,
                               beta)
           
            best_value = min(best_value, value)
            beta = min(beta, best_value)
            if beta <= alpha:
                break
        return best_value
print("Enter 8 leaf node values (space separated):")
leaf_values = list(map(int, input().split()))
result = alpha_beta(0, 0, True, leaf_values, -math.inf, math.inf)
print("Optimal value using Alpha-Beta Pruning is:", result)