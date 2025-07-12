"""
UI Only components
""" 

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
from graph_data import create_transportation_network, TransportationGraph
from typing import List, Dict, Tuple

class TransportationGUI:
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Transportation Network - Dijkstra's Algorithm")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize the transportation graph
        self.graph = create_transportation_network()
        self.current_path = []
        self.current_cost = 0
        
        # Create the GUI components
        self.create_widgets()
        self.create_graph_visualization()
        
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Create sections
        self.create_input_section(main_frame)
        self.create_results_section(main_frame)
        self.create_visualization_section(main_frame)
        self.create_data_table_section(main_frame)
        
    def create_input_section(self, parent):
        """Create input controls section"""
        input_frame = ttk.LabelFrame(parent, text="Route Planning", padding="10")
        input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Origin selection
        ttk.Label(input_frame, text="Origin:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.origin_var = tk.StringVar()
        self.origin_combo = ttk.Combobox(input_frame, textvariable=self.origin_var, 
                                        values=list(self.graph.nodes), state="readonly")
        self.origin_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Destination selection
        ttk.Label(input_frame, text="Destination:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.destination_var = tk.StringVar()
        self.destination_combo = ttk.Combobox(input_frame, textvariable=self.destination_var,
                                            values=list(self.graph.nodes), state="readonly")
        self.destination_combo.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Optimization type
        ttk.Label(input_frame, text="Optimize for:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        self.optimization_var = tk.StringVar(value="fare")
        opt_frame = ttk.Frame(input_frame)
        opt_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Radiobutton(opt_frame, text="Minimum Fare", variable=self.optimization_var, 
                       value="fare").grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(opt_frame, text="Shortest Distance", variable=self.optimization_var, 
                       value="distance").grid(row=0, column=1, sticky=tk.W, padx=(20, 0))
        
        # Buttons
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=1, column=2, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(button_frame, text="Find Route", command=self.find_route).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_frame, text="Clear", command=self.clear_results).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(button_frame, text="All Routes", command=self.show_all_routes).grid(row=0, column=2)
        
        # Configure column weights
        input_frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(3, weight=1)
        
    def create_results_section(self, parent):
        """Create results display section"""
        results_frame = ttk.LabelFrame(parent, text="Route Results", padding="10")
        results_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(1, weight=1)
        
        # Summary information
        self.summary_text = tk.Text(results_frame, height=4, wrap=tk.WORD)
        self.summary_text.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Route details
        ttk.Label(results_frame, text="Route Details:").grid(row=1, column=0, sticky=(tk.W, tk.N))
        
        # Create treeview for route details
        columns = ('Step', 'From', 'To', 'Distance (km)', 'Fare (pesos)')
        self.route_tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.route_tree.heading(col, text=col)
            self.route_tree.column(col, width=100)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.route_tree.yview)
        self.route_tree.configure(yscrollcommand=scrollbar.set)
        
        self.route_tree.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0))
        scrollbar.grid(row=2, column=1, sticky=(tk.N, tk.S), pady=(5, 0))
        
        # Export button
        ttk.Button(results_frame, text="Export Results", command=self.export_results).grid(row=3, column=0, pady=(10, 0))
        
    def create_visualization_section(self, parent):
        """Create graph visualization section"""
        viz_frame = ttk.LabelFrame(parent, text="Network Visualization", padding="10")
        viz_frame.grid(row=0, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        viz_frame.columnconfigure(0, weight=1)
        viz_frame.rowconfigure(0, weight=1)
        
        # Create matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(6, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, viz_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Visualization controls
        control_frame = ttk.Frame(viz_frame)
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(control_frame, text="Show All Routes", command=self.show_full_network).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(control_frame, text="Highlight Path", command=self.highlight_current_path).grid(row=0, column=1)
        
    def create_data_table_section(self, parent):
        """Create data table section"""
        table_frame = ttk.LabelFrame(parent, text="All Routes Data", padding="10")
        table_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Create treeview for all routes
        columns = ('Origin', 'Destination', 'Distance (km)', 'Fare (pesos)')
        self.data_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=6)
        
        for col in columns:
            self.data_tree.heading(col, text=col)
            self.data_tree.column(col, width=150)
        
        # Scrollbar for data table
        data_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.data_tree.yview)
        self.data_tree.configure(yscrollcommand=data_scrollbar.set)
        
        self.data_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        data_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Load data into table
        self.load_data_table()
        
    def create_graph_visualization(self):
        """Create the initial graph visualization"""
        self.show_full_network()
        
    def load_data_table(self):
        """Load all route data into the data table"""
        # Clear existing data
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
        
        # Add all routes
        written_edges = set()
        for node in self.graph.nodes:
            for neighbor, distance, fare in self.graph.get_neighbors(node):
                # Avoid duplicate edges
                edge = tuple(sorted([node, neighbor]))
                if edge not in written_edges:
                    self.data_tree.insert('', 'end', values=(node, neighbor, f"{distance:.1f}", f"{fare:.0f}"))
                    written_edges.add(edge)
                    
    def find_route(self):
        """Find and display the optimal route"""
        origin = self.origin_var.get()
        destination = self.destination_var.get()
        optimization = self.optimization_var.get()
        
        if not origin or not destination:
            messagebox.showwarning("Input Error", "Please select both origin and destination.")
            return
        
        if origin == destination:
            messagebox.showwarning("Input Error", "Origin and destination cannot be the same.")
            return
        
        # Find the route using Dijkstra's algorithm
        path, cost = self.graph.dijkstra(origin, destination, optimization)
        
        if not path:
            messagebox.showerror("No Route", "No route found between the selected locations.")
            return
        
        self.current_path = path
        self.current_cost = cost
        
        # Display results
        self.display_results(path, cost, optimization)
        self.highlight_current_path()
        
    def display_results(self, path: List[str], cost: float, optimization: str):
        """Display route results in the GUI"""
        # Clear previous results
        self.summary_text.delete(1.0, tk.END)
        for item in self.route_tree.get_children():
            self.route_tree.delete(item)
        
        # Display summary
        cost_unit = "pesos" if optimization == "fare" else "km"
        optimization_text = "Cheapest" if optimization == "fare" else "Shortest"
        
        summary = f"{optimization_text} route from {path[0]} to {path[-1]}:\n"
        summary += f"Route: {' → '.join(path)}\n"
        summary += f"Total {optimization}: {cost:.1f} {cost_unit}\n"
        summary += f"Number of stops: {len(path) - 1}"
        
        self.summary_text.insert(tk.END, summary)
        
        # Display route details
        details = self.graph.get_route_details(path)
        for i, detail in enumerate(details, 1):
            self.route_tree.insert('', 'end', values=(
                i, detail['from'], detail['to'], 
                f"{detail['distance']:.1f}", f"{detail['fare']:.0f}"
            ))
    
    def show_full_network(self):
        """Display the complete transportation network"""
        self.ax.clear()
        
        # Create NetworkX graph for visualization
        G = nx.Graph()
        
        # Add nodes with positions
        for node in self.graph.nodes:
            G.add_node(node, pos=self.graph.coordinates.get(node, (0, 0)))
        
        # Add edges
        for node in self.graph.nodes:
            for neighbor, distance, fare in self.graph.get_neighbors(node):
                if not G.has_edge(node, neighbor):  # Avoid duplicate edges
                    G.add_edge(node, neighbor, distance=distance, fare=fare)
        
        # Get positions
        pos = nx.get_node_attributes(G, 'pos')
        
        # Draw the network
        nx.draw(G, pos, ax=self.ax, with_labels=True, node_color='lightblue', 
                node_size=1500, font_size=8, font_weight='bold')
        
        # Add edge labels (distances and fares)
        edge_labels = {}
        for node in self.graph.nodes:
            for neighbor, distance, fare in self.graph.get_neighbors(node):
                if (node, neighbor) not in edge_labels and (neighbor, node) not in edge_labels:
                    edge_labels[(node, neighbor)] = f"{distance:.1f}km\n₱{fare:.0f}"
        
        nx.draw_networkx_edge_labels(G, pos, edge_labels, ax=self.ax, font_size=6)
        
        self.ax.set_title("Transportation Network")
        self.ax.set_aspect('equal')
        self.canvas.draw()
    
    def highlight_current_path(self):
        """Highlight the current path in the visualization"""
        if not self.current_path:
            return
        
        self.ax.clear()
        
        # Create NetworkX graph
        G = nx.Graph()
        
        # Add all nodes
        for node in self.graph.nodes:
            G.add_node(node, pos=self.graph.coordinates.get(node, (0, 0)))
        
        # Add all edges
        for node in self.graph.nodes:
            for neighbor, distance, fare in self.graph.get_neighbors(node):
                if not G.has_edge(node, neighbor):
                    G.add_edge(node, neighbor, distance=distance, fare=fare)
        
        pos = nx.get_node_attributes(G, 'pos')
        
        # Draw all edges in light gray
        nx.draw_networkx_edges(G, pos, ax=self.ax, edge_color='lightgray', width=1)
        
        # Draw path edges in red
        path_edges = [(self.current_path[i], self.current_path[i+1]) 
                     for i in range(len(self.current_path)-1)]
        nx.draw_networkx_edges(G, pos, edgelist=path_edges, ax=self.ax, 
                              edge_color='red', width=3)
        
        # Draw all nodes
        node_colors = ['red' if node in self.current_path else 'lightblue' 
                      for node in G.nodes()]
        nx.draw_networkx_nodes(G, pos, ax=self.ax, node_color=node_colors, 
                              node_size=1500)
        
        # Draw labels
        nx.draw_networkx_labels(G, pos, ax=self.ax, font_size=8, font_weight='bold')
        
        # Add edge labels for path only
        path_labels = {}
        for i in range(len(self.current_path)-1):
            current = self.current_path[i]
            next_node = self.current_path[i+1]
            for neighbor, distance, fare in self.graph.get_neighbors(current):
                if neighbor == next_node:
                    path_labels[(current, next_node)] = f"{distance:.1f}km\n₱{fare:.0f}"
                    break
        
        nx.draw_networkx_edge_labels(G, pos, path_labels, ax=self.ax, font_size=6)
        
        self.ax.set_title(f"Highlighted Path: {' → '.join(self.current_path)}")
        self.ax.set_aspect('equal')
        self.canvas.draw()
    
    def clear_results(self):
        """Clear all results and reset the interface"""
        self.summary_text.delete(1.0, tk.END)
        for item in self.route_tree.get_children():
            self.route_tree.delete(item)
        
        self.current_path = []
        self.current_cost = 0
        
        self.origin_var.set('')
        self.destination_var.set('')
        
        self.show_full_network()
    
    def show_all_routes(self):
        """Show all possible routes from selected origin"""
        origin = self.origin_var.get()
        if not origin:
            messagebox.showwarning("Input Error", "Please select an origin location.")
            return
        
        optimization = self.optimization_var.get()
        all_paths = self.graph.get_all_paths(origin, optimization)
        
        # Create a new window to display all routes
        self.show_all_routes_window(origin, all_paths, optimization)
    
    def show_all_routes_window(self, origin: str, all_paths: Dict, optimization: str):
        """Display all routes in a new window"""
        routes_window = tk.Toplevel(self.root)
        routes_window.title(f"All Routes from {origin}")
        routes_window.geometry("800x600")
        
        # Create treeview for all routes
        columns = ('Destination', 'Path', 'Cost', 'Steps')
        tree = ttk.Treeview(routes_window, columns=columns, show='headings')
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(routes_window, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate the tree
        cost_unit = "pesos" if optimization == "fare" else "km"
        for destination, (path, cost) in all_paths.items():
            if path:  # Only show reachable destinations
                tree.insert('', 'end', values=(
                    destination,
                    ' → '.join(path),
                    f"{cost:.1f} {cost_unit}",
                    len(path) - 1
                ))
    
    def export_results(self):
        """Export current results to a file"""
        if not self.current_path:
            messagebox.showwarning("No Results", "No route results to export.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write("Transportation Network Route Analysis\n")
                    f.write("=" * 50 + "\n\n")
                    
                    # Write summary
                    optimization = self.optimization_var.get()
                    cost_unit = "pesos" if optimization == "fare" else "km"
                    
                    f.write(f"Route: {' → '.join(self.current_path)}\n")
                    f.write(f"Total {optimization}: {self.current_cost:.1f} {cost_unit}\n")
                    f.write(f"Number of stops: {len(self.current_path) - 1}\n\n")
                    
                    # Write detailed route
                    f.write("Detailed Route:\n")
                    f.write("-" * 20 + "\n")
                    
                    details = self.graph.get_route_details(self.current_path)
                    for i, detail in enumerate(details, 1):
                        f.write(f"Step {i}: {detail['from']} → {detail['to']}\n")
                        f.write(f"  Distance: {detail['distance']:.1f} km\n")
                        f.write(f"  Fare: ₱{detail['fare']:.0f}\n\n")
                
                messagebox.showinfo("Export Successful", f"Results exported to {filename}")
                
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export results: {str(e)}")
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()


class NetworkAnalysisWindow:
    """Additional window for network analysis and statistics"""
    
    def __init__(self, parent_app):
        self.parent = parent_app
        self.graph = parent_app.graph
        self.window = tk.Toplevel(parent_app.root)
        self.window.title("Network Analysis")
        self.window.geometry("600x500")
        
        self.create_analysis_widgets()
        self.perform_analysis()
    
    def create_analysis_widgets(self):
        """Create widgets for network analysis"""
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Analysis results text area
        self.analysis_text = tk.Text(main_frame, wrap=tk.WORD, height=25)
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.analysis_text.yview)
        self.analysis_text.configure(yscrollcommand=scrollbar.set)
        
        self.analysis_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons frame
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="Refresh Analysis", 
                  command=self.perform_analysis).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Export Analysis", 
                  command=self.export_analysis).pack(side=tk.LEFT)
    
    def perform_analysis(self):
        """Perform comprehensive network analysis"""
        self.analysis_text.delete(1.0, tk.END)
        
        analysis = "TRANSPORTATION NETWORK ANALYSIS\n"
        analysis += "=" * 50 + "\n\n"
        
        # Basic network statistics
        analysis += "BASIC NETWORK STATISTICS\n"
        analysis += "-" * 30 + "\n"
        analysis += f"Total nodes: {len(self.graph.nodes)}\n"
        analysis += f"Total connections: {sum(len(neighbors) for neighbors in self.graph.edges.values()) // 2}\n"
        analysis += f"Nodes: {', '.join(sorted(self.graph.nodes))}\n\n"
        
        # Distance and fare statistics
        distances = []
        fares = []
        
        for node in self.graph.nodes:
            for neighbor, distance, fare in self.graph.get_neighbors(node):
                distances.append(distance)
                fares.append(fare)
        
        # Remove duplicates (since graph is undirected)
        distances = list(set(distances))
        fares = list(set(fares))
        
        analysis += "DISTANCE STATISTICS\n"
        analysis += "-" * 20 + "\n"
        analysis += f"Average distance: {sum(distances) / len(distances):.1f} km\n"
        analysis += f"Shortest route: {min(distances):.1f} km\n"
        analysis += f"Longest route: {max(distances):.1f} km\n\n"
        
        analysis += "FARE STATISTICS\n"
        analysis += "-" * 15 + "\n"
        analysis += f"Average fare: ₱{sum(fares) / len(fares):.1f}\n"
        analysis += f"Cheapest fare: ₱{min(fares):.0f}\n"
        analysis += f"Most expensive fare: ₱{max(fares):.0f}\n\n"
        
        # Connectivity analysis
        analysis += "CONNECTIVITY ANALYSIS\n"
        analysis += "-" * 22 + "\n"
        for node in sorted(self.graph.nodes):
            connections = len(self.graph.get_neighbors(node))
            analysis += f"{node}: {connections} direct connections\n"
        
        analysis += "\nMOST CONNECTED NODES\n"
        analysis += "-" * 20 + "\n"
        node_connections = [(node, len(self.graph.get_neighbors(node))) 
                           for node in self.graph.nodes]
        node_connections.sort(key=lambda x: x[1], reverse=True)
        
        for node, count in node_connections[:3]:
            analysis += f"{node}: {count} connections\n"
        
        # Route efficiency analysis
        analysis += "\nROUTE EFFICIENCY ANALYSIS\n"
        analysis += "-" * 26 + "\n"
        
        # Find most efficient routes (best fare per km)
        route_efficiency = []
        written_edges = set()
        
        for node in self.graph.nodes:
            for neighbor, distance, fare in self.graph.get_neighbors(node):
                edge = tuple(sorted([node, neighbor]))
                if edge not in written_edges:
                    efficiency = fare / distance if distance > 0 else 0
                    route_efficiency.append((f"{node} ↔ {neighbor}", efficiency, distance, fare))
                    written_edges.add(edge)
        
        route_efficiency.sort(key=lambda x: x[1])
        
        analysis += "Most efficient routes (lowest fare per km):\n"
        for route, efficiency, distance, fare in route_efficiency[:3]:
            analysis += f"{route}: ₱{efficiency:.1f}/km ({distance:.1f}km, ₱{fare:.0f})\n"
        
        analysis += "\nLeast efficient routes (highest fare per km):\n"
        for route, efficiency, distance, fare in route_efficiency[-3:]:
            analysis += f"{route}: ₱{efficiency:.1f}/km ({distance:.1f}km, ₱{fare:.0f})\n"
        
        self.analysis_text.insert(tk.END, analysis)
    
    def export_analysis(self):
        """Export network analysis to file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.analysis_text.get(1.0, tk.END))
                messagebox.showinfo("Export Successful", f"Analysis exported to {filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export analysis: {str(e)}")


def main():
    """Main function to run the application"""
    try:
        app = TransportationGUI()
        
        # Add menu bar
        menubar = tk.Menu(app.root)
        app.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Graph Data", command=lambda: app.graph.export_to_csv("transportation_data.csv"))
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=app.root.quit)
        
        # Analysis menu
        analysis_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Analysis", menu=analysis_menu)
        analysis_menu.add_command(label="Network Statistics", command=lambda: NetworkAnalysisWindow(app))
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=lambda: messagebox.showinfo(
            "About", "Transportation Network Analysis\nUsing Dijkstra's Algorithm\n\n"))
        
        app.run()
        
    except Exception as e:
        messagebox.showerror("Application Error", f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()