import heapq

def a_star_search(graph, start_node: str, goal_node: str):
    """
    Algoritma A* Search berbasis heapq untuk mencari alokasi slot reschedule optimal.
    """
    # Priority Queue menyimpan tuple: (f_score, g_score, current_node, path)
    priority_queue = []
    heapq.heappush(priority_queue, (0, 0, start_node, [start_node]))
    
    visited = {}

    while priority_queue:
        f_score, g_score, current, path = heapq.heappop(priority_queue)

        if current == goal_node:
            return path, g_score

        if current in visited and visited[current] <= g_score:
            continue

        visited[current] = g_score

        for neighbor, weight in graph.get_neighbors(current):
            tentative_g = g_score + weight
            h_score = graph.heuristic(neighbor, goal_node)
            f_neighbor = tentative_g + h_score

            if neighbor not in visited or tentative_g < visited[neighbor]:
                heapq.heappush(priority_queue, (f_neighbor, tentative_g, neighbor, path + [neighbor]))

    return None, float("inf")