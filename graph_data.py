"""
Transportation Graph Data Structure
Contains the graph implementation and transportation network data
"""

import heapq
from typing import Dict, List, Tuple, Optional
import csv
import json
import datetime

class TransportationGraph:
    """
    Graph implementation for transportation network using Dijkstra's algorithm
    """
    
    def __init__(self):
        self.nodes = set()
        self.edges = {}  # adjacency list: {node: [(neighbor, distance, fare), ...]}
        self.coordinates = {}  # For visualization: {node: (x, y)}
        
    def add_node(self, node: str, coordinates: Optional[Tuple[float, float]] = None):
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
        with open(filename, 'w', newline='', encoding='utf-8') as file:
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
        self.nodes = set()
        self.edges = {}
        self.coordinates = {}
        
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                origin = (row.get('Origin') or row.get('origin') or row.get('From') or row.get('from') or '').strip()
                destination = (row.get('Destination') or row.get('destination') or row.get('To') or row.get('to') or '').strip()
                distance_str = row.get('Distance_km') or row.get('Distance (km)') or row.get('distance') or row.get('Distance') or '0'
                fare_str = row.get('Fare_pesos') or row.get('Fare (₱)') or row.get('Fare (pesos)') or row.get('fare') or row.get('Fare') or '0'
                
                if origin and destination:
                    distance = float(distance_str)
                    fare = float(fare_str)
                    self.add_edge(origin, destination, distance, fare)
    
    def export_to_json(self, filename: str):
        """Export graph data to JSON file"""
        routes = []
        written_edges = set()
        
        for node in self.nodes:
            for neighbor, distance, fare in self.get_neighbors(node):
                edge = tuple(sorted([node, neighbor]))
                if edge not in written_edges:
                    routes.append({
                        'origin': node,
                        'destination': neighbor,
                        'distance': distance,
                        'fare': fare
                    })
                    written_edges.add(edge)
        
        data = {
            'metadata': {
                'description': 'Transportation Network Data',
                'total_nodes': len(self.nodes),
                'total_routes': len(routes),
                'export_timestamp': datetime.datetime.now().isoformat(),
                'nodes': list(self.nodes)
            },
            'routes': routes
        }
        
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
    
    def import_from_json(self, filename: str):
        """Import graph data from JSON file"""
        self.nodes = set()
        self.edges = {}
        self.coordinates = {}
        
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Handle different JSON structures
        if 'routes' in data:
            routes = data['routes']
        elif 'edges' in data:
            routes = data['edges']
        else:
            routes = data
        
        for route in routes:
            origin = route['origin']
            destination = route['destination']
            distance = float(route['distance'])
            fare = float(route['fare'])
            
            self.add_edge(origin, destination, distance, fare)
    
    def get_network_statistics(self) -> Dict:
        """Get comprehensive network statistics"""
        if not self.nodes:
            return {}
        
        # Collect all distances and fares
        distances = []
        fares = []
        efficiencies = []
        
        written_edges = set()
        for node in self.nodes:
            for neighbor, distance, fare in self.get_neighbors(node):
                edge = tuple(sorted([node, neighbor]))
                if edge not in written_edges:
                    distances.append(distance)
                    fares.append(fare)
                    if distance > 0:
                        efficiencies.append(fare / distance)
                    written_edges.add(edge)
        
        # Calculate statistics
        stats = {
            'total_nodes': len(self.nodes),
            'total_edges': len(distances),
            'nodes': sorted(list(self.nodes)),
            'distance_stats': {
                'min': min(distances) if distances else 0,
                'max': max(distances) if distances else 0,
                'avg': sum(distances) / len(distances) if distances else 0,
                'total': sum(distances)
            },
            'fare_stats': {
                'min': min(fares) if fares else 0,
                'max': max(fares) if fares else 0,
                'avg': sum(fares) / len(fares) if fares else 0,
                'total': sum(fares)
            },
            'efficiency_stats': {
                'min': min(efficiencies) if efficiencies else 0,
                'max': max(efficiencies) if efficiencies else 0,
                'avg': sum(efficiencies) / len(efficiencies) if efficiencies else 0
            },
            'connectivity': {node: len(self.get_neighbors(node)) for node in self.nodes}
        }
        
        return stats


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


def test_dijkstra_comprehensive():
    """Comprehensive test of the Dijkstra algorithm implementation"""
    print("=" * 60)
    print("TRANSPORTATION NETWORK ANALYSIS - ALGORITHM VERIFICATION")
    print("=" * 60)
    
    graph = create_transportation_network()
    
    # Display network statistics
    stats = graph.get_network_statistics()
    print(f"\nNetwork Overview:")
    print(f"• Total locations: {stats['total_nodes']}")
    print(f"• Total routes: {stats['total_edges']}")
    print(f"• Locations: {', '.join(stats['nodes'])}")
    
    print(f"\nDistance Statistics:")
    print(f"• Shortest route: {stats['distance_stats']['min']:.1f} km")
    print(f"• Longest route: {stats['distance_stats']['max']:.1f} km")
    print(f"• Average distance: {stats['distance_stats']['avg']:.1f} km")
    
    print(f"\nFare Statistics:")
    print(f"• Cheapest fare: ₱{stats['fare_stats']['min']:.0f}")
    print(f"• Most expensive fare: ₱{stats['fare_stats']['max']:.0f}")
    print(f"• Average fare: ₱{stats['fare_stats']['avg']:.1f}")
    
    print(f"\nEfficiency Statistics (₱/km):")
    print(f"• Most efficient: ₱{stats['efficiency_stats']['min']:.1f}/km")
    print(f"• Least efficient: ₱{stats['efficiency_stats']['max']:.1f}/km")
    print(f"• Average efficiency: ₱{stats['efficiency_stats']['avg']:.1f}/km")
    
    # Test specific routes
    test_cases = [
        ("Tagoloan", "Indahag", "fare"),
        ("Tagoloan", "Indahag", "distance"),
        ("Gusa", "Taguanao", "fare"),
        ("Gusa", "Taguanao", "distance"),
        ("Balulang", "Iponan", "fare"),
        ("Carmen", "Pagatpat", "distance")
    ]
    
    print("\n" + "=" * 60)
    print("ROUTE OPTIMIZATION TESTS")
    print("=" * 60)
    
    for origin, destination, optimization in test_cases:
        print(f"\n🚌 Route: {origin} → {destination} (optimize for {optimization})")
        print("-" * 50)
        
        path, cost = graph.dijkstra(origin, destination, optimization)
        
        if path:
            print(f"✅ Path found: {' → '.join(path)}")
            cost_unit = "pesos" if optimization == "fare" else "km"
            print(f"💰 Total {optimization}: {cost:.1f} {cost_unit}")
            print(f"📍 Stops: {len(path) - 1}")
            
            # Show detailed route breakdown
            details = graph.get_route_details(path)
            total_distance = sum(detail['distance'] for detail in details)
            total_fare = sum(detail['fare'] for detail in details)
            
            print(f"📊 Route breakdown:")
            for i, detail in enumerate(details, 1):
                print(f"   {i}. {detail['from']} → {detail['to']}: "
                      f"{detail['distance']:.1f}km, ₱{detail['fare']:.0f}")
            
            print(f"📈 Summary: {total_distance:.1f}km total, ₱{total_fare:.0f} total")
            if total_distance > 0:
                print(f"⚡ Efficiency: ₱{total_fare/total_distance:.1f} per km")
        else:
            print("❌ No path found!")
    
    print("\n" + "=" * 60)
    print("ALGORITHM VERIFICATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    test_dijkstra_comprehensive()