"""
Transportation Graph Data Structure
Contains the graph implementation and transportation network data
"""

import heapq
from typing import Dict, List, Tuple, Optional
import csv
import json

class TransportationGraph:
    """
    Graph implementation for transportation network using Dijkstra's algorithm
    """
    
    def __init__(self):
        self.nodes = set()
        self.edges = {}  # adjacency list: {node: [(neighbor, distance, fare), ...]}
        self.coordinates = {}  # For visualization: {node: (x, y)}
        
    def add_node(self, node: str, coordinates: Tuple[float, float] = None):
        """Add a node to the graph"""
        self.nodes.add(node)
        if node not in self.edges:
            self.edges[node] = []
        if coordinates:
            self.coordinates[node] = coordinates
            
    def add_edge(self, source: str, destination: str, distance: float, fare: float):
        """Add an edge between two nodes (bidirectional)"""
        # Add both nodes if they don't exist
        self.add_node(source)
        self.add_node(destination)
        
        # Add edge in both directions (undirected graph)
        self.edges[source].append((destination, distance, fare))
        self.edges[destination].append((source, distance, fare))
        
    def get_neighbors(self, node: str) -> List[Tuple[str, float, float]]:
        """Get all neighbors of a node with their distances and fares"""
        return self.edges.get(node, [])
        
    def dijkstra(self, start: str, end: str, weight_type: str = 'fare') -> Tuple[List[str], float]:
        """
        Implement Dijkstra's algorithm to find shortest path
        
        Args:
            start: Starting node
            end: Destination node
            weight_type: 'fare' or 'distance' - what to optimize for
            
        Returns:
            Tuple of (path_list, total_cost)
        """
        if start not in self.nodes or end not in self.nodes:
            return [], float('inf')
            
        # Priority queue: (cost, node, path)
        pq = [(0, start, [start])]
        visited = set()
        distances = {node: float('inf') for node in self.nodes}
        distances[start] = 0
        
        while pq:
            current_cost, current_node, path = heapq.heappop(pq)
            
            if current_node in visited:
                continue
                
            visited.add(current_node)
            
            # If we reached the destination
            if current_node == end:
                return path, current_cost
                
            # Check all neighbors
            for neighbor, distance, fare in self.get_neighbors(current_node):
                if neighbor not in visited:
                    # Choose weight based on optimization type
                    weight = fare if weight_type == 'fare' else distance
                    new_cost = current_cost + weight
                    
                    if new_cost < distances[neighbor]:
                        distances[neighbor] = new_cost
                        new_path = path + [neighbor]
                        heapq.heappush(pq, (new_cost, neighbor, new_path))
        
        return [], float('inf')  # No path found
        
    def get_all_paths(self, start: str, weight_type: str = 'fare') -> Dict[str, Tuple[List[str], float]]:
        """Get shortest paths from start to all other nodes"""
        paths = {}
        for node in self.nodes:
            if node != start:
                path, cost = self.dijkstra(start, node, weight_type)
                paths[node] = (path, cost)
        return paths
        
    def get_route_details(self, path: List[str]) -> List[Dict]:
        """Get detailed information about a route"""
        if len(path) < 2:
            return []
            
        details = []
        total_distance = 0
        total_fare = 0
        
        for i in range(len(path) - 1):
            current = path[i]
            next_node = path[i + 1]
            
            # Find the edge between current and next
            for neighbor, distance, fare in self.get_neighbors(current):
                if neighbor == next_node:
                    details.append({
                        'from': current,
                        'to': next_node,
                        'distance': distance,
                        'fare': fare
                    })
                    total_distance += distance
                    total_fare += fare
                    break
                    
        return details
        
    def export_to_csv(self, filename: str):
        """Export graph data to CSV file"""
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Origin', 'Destination', 'Distance_km', 'Fare_pesos'])
            
            written_edges = set()
            for node in self.nodes:
                for neighbor, distance, fare in self.get_neighbors(node):
                    # Avoid duplicate edges (since graph is undirected)
                    edge = tuple(sorted([node, neighbor]))
                    if edge not in written_edges:
                        writer.writerow([node, neighbor, distance, fare])
                        written_edges.add(edge)
                        
    def import_from_csv(self, filename: str):
        """Import graph data from CSV file"""
        with open(filename, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                self.add_edge(
                    row['Origin'],
                    row['Destination'],
                    float(row['Distance_km']),
                    float(row['Fare_pesos'])
                )


def create_transportation_network() -> TransportationGraph:
    """
    Create the transportation network based on the provided data
    """
    graph = TransportationGraph()
    
    # Add all nodes with approximate coordinates for visualization
    nodes_coords = {
        'Tagoloan': (0, 0),
        'Gusa': (20, 10),
        'Balulang': (10, 5),
        'Carmen': (25, 0),
        'Pagatpat': (15, 15),
        'Iponan': (30, 20),
        'Indahag': (35, 25),
        'Taguanao': (25, 30)
    }
    
    for node, coords in nodes_coords.items():
        graph.add_node(node, coords)
    
    # Add edges based on the provided data
    routes = [
        ('Tagoloan', 'Gusa', 22.9, 30),
        ('Tagoloan', 'Balulang', 15.5, 25),
        ('Tagoloan', 'Carmen', 30.0, 40),
        ('Gusa', 'Balulang', 10.0, 15),
        ('Gusa', 'Carmen', 20.0, 25),
        ('Balulang', 'Pagatpat', 12.0, 20),
        ('Carmen', 'Iponan', 18.0, 35),
        ('Pagatpat', 'Taguanao', 25.0, 30),
        ('Iponan', 'Indahag', 14.0, 20),
        ('Taguanao', 'Indahag', 16.0, 25)
    ]
    
    for origin, destination, distance, fare in routes:
        graph.add_edge(origin, destination, distance, fare)
    
    return graph


def test_dijkstra():
    # debug hahahahaha
    graph = create_transportation_network()
    
    # Test shortest path by fare
    path, cost = graph.dijkstra('Tagoloan', 'Indahag', 'fare')
    print(f"Cheapest route from Tagoloan to Indahag: {' -> '.join(path)}")
    print(f"Total fare: {cost} pesos")
    
    # Test shortest path by distance
    path, cost = graph.dijkstra('Tagoloan', 'Indahag', 'distance')
    print(f"Shortest route from Tagoloan to Indahag: {' -> '.join(path)}")
    print(f"Total distance: {cost} km")
    
    # Get route details
    details = graph.get_route_details(path)
    print("Route details:")
    for detail in details:
        print(f"  {detail['from']} -> {detail['to']}: {detail['distance']} km, {detail['fare']} pesos")


if __name__ == "__main__":
    test_dijkstra()