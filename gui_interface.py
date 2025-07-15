"""
UI Only components - Enhanced with responsive design and import/export functionality
""" 

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
from graph_data import create_transportation_network, TransportationGraph
from typing import List, Dict, Tuple
import csv
import json
import os

class TransportationGUI:
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Transportation Network Analysis - Dijkstra's Algorithm")
        self.root.geometry("1400x900")
        self.root.minsize(1000, 700)  # Set minimum window size
        self.root.configure(bg='#f5f5f5')
        
        # Configure main window grid weights for responsive design
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Initialize the transportation graph
        self.graph = create_transportation_network()
        self.current_path = []
        self.current_cost = 0
        
        # Configure ttk style for better appearance
        self.setup_styles()
        
        # Create the GUI components
        self.create_widgets()
        self.create_graph_visualization()
        self.create_menu_bar()
        
    def setup_styles(self):
        """Configure custom styles for better appearance"""
        style = ttk.Style()
        
        # Configure modern style theme
        if 'clam' in style.theme_names():
            style.theme_use('clam')
        
        # Custom button style
        style.configure('Action.TButton', 
                       font=('Segoe UI', 9, 'bold'),
                       padding=(10, 5))
        
        # Custom labelframe style
        style.configure('Card.TLabelframe', 
                       background='#ffffff',
                       relief='solid',
                       borderwidth=1)
        
        # Custom labelframe label style
        style.configure('Card.TLabelframe.Label',
                       font=('Segoe UI', 10, 'bold'),
                       background='#ffffff',
                       foreground='#2c3e50')
        
    def create_menu_bar(self):
        """Create enhanced menu bar with import/export options"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Import Data...", command=self.import_data, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Export Data as CSV...", command=self.export_data_csv, accelerator="Ctrl+S")
        file_menu.add_command(label="Export Data as JSON...", command=self.export_data_json)
        file_menu.add_command(label="Export Results...", command=self.export_results, accelerator="Ctrl+E")
        file_menu.add_separator()
        file_menu.add_command(label="Reset to Default Data", command=self.reset_to_default)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Ctrl+Q")
        
        # Analysis menu
        analysis_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Analysis", menu=analysis_menu)
        analysis_menu.add_command(label="Network Statistics", command=lambda: NetworkAnalysisWindow(self))
        analysis_menu.add_command(label="All Routes Matrix", command=self.show_all_routes_matrix)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Show Full Network", command=self.show_full_network)
        view_menu.add_command(label="Refresh Data Table", command=self.load_data_table)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="User Guide", command=self.show_user_guide)
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-o>', lambda e: self.import_data())
        self.root.bind('<Control-s>', lambda e: self.export_data_csv())
        self.root.bind('<Control-e>', lambda e: self.export_results())
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        
    def create_widgets(self):
        """Create all GUI widgets with responsive design"""
        # Main container with padding
        main_container = ttk.Frame(self.root, padding="15")
        main_container.grid(row=0, column=0, sticky="nsew")
        
        # Configure main container grid weights for responsive design
        main_container.columnconfigure(0, weight=2)  # Left side (controls + results)
        main_container.columnconfigure(1, weight=3)  # Right side (visualization)
        main_container.rowconfigure(0, weight=0)     # Input section (fixed height)
        main_container.rowconfigure(1, weight=1)     # Results and visualization
        main_container.rowconfigure(2, weight=1)     # Data table
        
        # Create sections with proper grid configuration
        self.create_input_section(main_container)
        self.create_results_section(main_container)
        self.create_visualization_section(main_container)
        self.create_data_table_section(main_container)
        
    def create_input_section(self, parent):
        """Create enhanced input controls section"""
        input_frame = ttk.LabelFrame(parent, text="🚌 Route Planning", padding="15", style='Card.TLabelframe')
        input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Configure input frame grid weights
        input_frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(3, weight=1)
        input_frame.columnconfigure(5, weight=1)
        
        # Row 1: Origin and Destination
        ttk.Label(input_frame, text="From:", font=('Segoe UI', 9, 'bold')).grid(
            row=0, column=0, sticky=tk.W, padx=(0, 8), pady=(0, 10))
        
        self.origin_var = tk.StringVar()
        self.origin_combo = ttk.Combobox(input_frame, textvariable=self.origin_var, 
                                        values=sorted(list(self.graph.nodes)), state="readonly",
                                        font=('Segoe UI', 9), width=15)
        self.origin_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 20), pady=(0, 10))
        
        ttk.Label(input_frame, text="To:", font=('Segoe UI', 9, 'bold')).grid(
            row=0, column=2, sticky=tk.W, padx=(0, 8), pady=(0, 10))
        
        self.destination_var = tk.StringVar()
        self.destination_combo = ttk.Combobox(input_frame, textvariable=self.destination_var,
                                            values=sorted(list(self.graph.nodes)), state="readonly",
                                            font=('Segoe UI', 9), width=15)
        self.destination_combo.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=(0, 20), pady=(0, 10))
        
        # Quick swap button
        ttk.Button(input_frame, text="⇄", command=self.swap_locations, width=3).grid(
            row=0, column=4, padx=(0, 20), pady=(0, 10))
        
        # Row 2: Optimization options
        ttk.Label(input_frame, text="Optimize for:", font=('Segoe UI', 9, 'bold')).grid(
            row=1, column=0, sticky=tk.W, padx=(0, 8), pady=(0, 10))
        
        self.optimization_var = tk.StringVar(value="fare")
        opt_frame = ttk.Frame(input_frame)
        opt_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Radiobutton(opt_frame, text="💰 Minimum Fare", variable=self.optimization_var, 
                       value="fare", style='TRadiobutton').grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(opt_frame, text="📏 Shortest Distance", variable=self.optimization_var, 
                       value="distance", style='TRadiobutton').grid(row=0, column=1, sticky=tk.W, padx=(25, 0))
        
        # Action buttons
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=1, column=2, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(button_frame, text="🔍 Find Route", command=self.find_route, 
                  style='Action.TButton').grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_frame, text="🗑️ Clear", command=self.clear_results).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(button_frame, text="📊 All Routes", command=self.show_all_routes).grid(row=0, column=2, padx=(0, 10))
        ttk.Button(button_frame, text="📈 Compare Routes", command=self.compare_routes).grid(row=0, column=3)
        
    def create_results_section(self, parent):
        """Create enhanced results display section"""
        results_frame = ttk.LabelFrame(parent, text="📋 Route Results", padding="15", style='Card.TLabelframe')
        results_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15), padx=(0, 15))
        
        # Configure results frame grid weights
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(1, weight=1)
        
        # Summary information with enhanced styling
        summary_label = ttk.Label(results_frame, text="Route Summary:", font=('Segoe UI', 10, 'bold'))
        summary_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 8))
        
        # Create frame for summary text with border
        summary_container = ttk.Frame(results_frame, relief='solid', borderwidth=1)
        summary_container.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(25, 15))
        summary_container.columnconfigure(0, weight=1)
        
        self.summary_text = tk.Text(summary_container, height=5, wrap=tk.WORD, 
                                   font=('Consolas', 9), bg='#f8f9fa', 
                                   relief='flat', padx=10, pady=8)
        self.summary_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Route details with enhanced treeview
        details_label = ttk.Label(results_frame, text="Detailed Route Steps:", font=('Segoe UI', 10, 'bold'))
        details_label.grid(row=1, column=0, sticky="nw", pady=(0, 8))
        
        # Create container for treeview
        tree_container = ttk.Frame(results_frame)
        tree_container.grid(row=1, column=0, sticky="nsew", pady=(25, 0))
        tree_container.columnconfigure(0, weight=1)
        tree_container.rowconfigure(0, weight=1)
        
        # Enhanced treeview with better columns
        columns = ('Step', 'From', 'To', 'Distance (km)', 'Fare (₱)', 'Cumulative')
        self.route_tree = ttk.Treeview(tree_container, columns=columns, show='headings', height=10)
        
        # Configure column widths and alignment
        column_widths = {'Step': 60, 'From': 100, 'To': 100, 'Distance (km)': 100, 'Fare (₱)': 80, 'Cumulative': 100}
        for col in columns:
            self.route_tree.heading(col, text=col, anchor='center')
            self.route_tree.column(col, width=column_widths.get(col, 100), anchor='center')
        
        # Scrollbars for treeview
        v_scrollbar = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.route_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL, command=self.route_tree.xview)
        self.route_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.route_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
    def create_visualization_section(self, parent):
        """Create enhanced graph visualization section"""
        viz_frame = ttk.LabelFrame(parent, text="🗺️ Network Visualization", padding="15", style='Card.TLabelframe')
        viz_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure visualization frame grid weights
        viz_frame.columnconfigure(0, weight=1)
        viz_frame.rowconfigure(0, weight=1)
        
        # Create matplotlib figure with better DPI
        plt.style.use('default')  # Reset to default style
        self.fig, self.ax = plt.subplots(figsize=(8, 6), dpi=100, facecolor='white')
        self.fig.patch.set_facecolor('white')
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, viz_frame)
        self.canvas.get_tk_widget().configure(bg='white')
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Enhanced visualization controls
        control_frame = ttk.Frame(viz_frame)
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(control_frame, text="🌐 Show Full Network", 
                  command=self.show_full_network).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(control_frame, text="🎯 Highlight Path", 
                  command=self.highlight_current_path).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(control_frame, text="💾 Save Image", 
                  command=self.save_network_image).grid(row=0, column=2)
        
    def create_data_table_section(self, parent):
        """Create enhanced data table section"""
        table_frame = ttk.LabelFrame(parent, text="📊 Transportation Network Data", padding="15", style='Card.TLabelframe')
        table_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(15, 0))
        
        # Configure table frame grid weights
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(1, weight=1)
        
        # Control buttons for data management
        control_frame = ttk.Frame(table_frame)
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(control_frame, text="📁 Import Data", command=self.import_data).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(control_frame, text="📤 Export CSV", command=self.export_data_csv).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(control_frame, text="🔄 Refresh", command=self.load_data_table).grid(row=0, column=2, padx=(0, 10))
        
        # Data count label
        self.data_count_label = ttk.Label(control_frame, text="", font=('Segoe UI', 9))
        self.data_count_label.grid(row=0, column=3, padx=(20, 0))
        
        # Enhanced data table container
        table_container = ttk.Frame(table_frame)
        table_container.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        table_container.columnconfigure(0, weight=1)
        table_container.rowconfigure(0, weight=1)
        
        # Enhanced treeview for all routes
        columns = ('Origin', 'Destination', 'Distance (km)', 'Fare (₱)', 'Efficiency (₱/km)')
        self.data_tree = ttk.Treeview(table_container, columns=columns, show='headings', height=8)
        
        # Configure data table columns
        column_widths = {'Origin': 150, 'Destination': 150, 'Distance (km)': 120, 'Fare (₱)': 100, 'Efficiency (₱/km)': 130}
        for col in columns:
            self.data_tree.heading(col, text=col, anchor='center')
            self.data_tree.column(col, width=column_widths.get(col, 120), anchor='center')
        
        # Scrollbars for data table
        data_v_scrollbar = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=self.data_tree.yview)
        data_h_scrollbar = ttk.Scrollbar(table_container, orient=tk.HORIZONTAL, command=self.data_tree.xview)
        self.data_tree.configure(yscrollcommand=data_v_scrollbar.set, xscrollcommand=data_h_scrollbar.set)
        
        self.data_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        data_v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        data_h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Load initial data
        self.load_data_table()
        
    def create_graph_visualization(self):
        """Create the initial graph visualization"""
        self.show_full_network()
        
    def load_data_table(self):
        """Load all route data into the data table with efficiency calculation"""
        # Clear existing data
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
        
        # Add all routes with efficiency calculation
        written_edges = set()
        route_count = 0
        
        for node in self.graph.nodes:
            for neighbor, distance, fare in self.graph.get_neighbors(node):
                # Avoid duplicate edges
                edge = tuple(sorted([node, neighbor]))
                if edge not in written_edges:
                    efficiency = fare / distance if distance > 0 else 0
                    self.data_tree.insert('', 'end', values=(
                        node, neighbor, f"{distance:.1f}", f"{fare:.0f}", f"{efficiency:.1f}"
                    ))
                    written_edges.add(edge)
                    route_count += 1
        
        # Update count label
        self.data_count_label.config(text=f"Total routes: {route_count}")
    
    def swap_locations(self):
        """Swap origin and destination"""
        origin = self.origin_var.get()
        destination = self.destination_var.get()
        self.origin_var.set(destination)
        self.destination_var.set(origin)
    
    def compare_routes(self):
        """Compare different route options"""
        origin = self.origin_var.get()
        destination = self.destination_var.get()
        
        if not origin or not destination:
            messagebox.showwarning("Input Error", "Please select both origin and destination.")
            return
        
        if origin == destination:
            messagebox.showwarning("Input Error", "Origin and destination cannot be the same.")
            return
        
        # Find routes for both optimization types
        fare_path, fare_cost = self.graph.dijkstra(origin, destination, 'fare')
        distance_path, distance_cost = self.graph.dijkstra(origin, destination, 'distance')
        
        if not fare_path or not distance_path:
            messagebox.showerror("No Route", "No route found between the selected locations.")
            return
        
        # Create comparison window
        self.show_route_comparison(origin, destination, fare_path, fare_cost, distance_path, distance_cost)
    
    def show_route_comparison(self, origin, destination, fare_path, fare_cost, distance_path, distance_cost):
        """Show route comparison in a new window"""
        comp_window = tk.Toplevel(self.root)
        comp_window.title(f"Route Comparison: {origin} → {destination}")
        comp_window.geometry("900x600")
        comp_window.configure(bg='#f5f5f5')
        
        # Main container
        main_frame = ttk.Frame(comp_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text=f"Route Comparison: {origin} → {destination}", 
                               font=('Segoe UI', 14, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Create two comparison frames
        comparison_frame = ttk.Frame(main_frame)
        comparison_frame.pack(fill=tk.BOTH, expand=True)
        
        # Cheapest route frame
        fare_frame = ttk.LabelFrame(comparison_frame, text="💰 Cheapest Route (by Fare)", padding="15")
        fare_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        fare_details = self.graph.get_route_details(fare_path)
        total_distance = sum(detail['distance'] for detail in fare_details)
        
        fare_info = f"Route: {' → '.join(fare_path)}\n"
        fare_info += f"Total Fare: ₱{fare_cost:.0f}\n"
        fare_info += f"Total Distance: {total_distance:.1f} km\n"
        fare_info += f"Steps: {len(fare_path) - 1}"
        
        fare_text = tk.Text(fare_frame, height=4, wrap=tk.WORD, font=('Consolas', 9))
        fare_text.insert(tk.END, fare_info)
        fare_text.config(state=tk.DISABLED)
        fare_text.pack(fill=tk.X, pady=(0, 10))
        
        # Shortest route frame
        distance_frame = ttk.LabelFrame(comparison_frame, text="📏 Shortest Route (by Distance)", padding="15")
        distance_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        distance_details = self.graph.get_route_details(distance_path)
        total_fare = sum(detail['fare'] for detail in distance_details)
        
        distance_info = f"Route: {' → '.join(distance_path)}\n"
        distance_info += f"Total Distance: {distance_cost:.1f} km\n"
        distance_info += f"Total Fare: ₱{total_fare:.0f}\n"
        distance_info += f"Steps: {len(distance_path) - 1}"
        
        distance_text = tk.Text(distance_frame, height=4, wrap=tk.WORD, font=('Consolas', 9))
        distance_text.insert(tk.END, distance_info)
        distance_text.config(state=tk.DISABLED)
        distance_text.pack(fill=tk.X, pady=(0, 10))
        
        # Analysis
        analysis_frame = ttk.LabelFrame(main_frame, text="📊 Analysis", padding="15")
        analysis_frame.pack(fill=tk.X, pady=(20, 0))
        
        if fare_path == distance_path:
            analysis = "✅ Both optimization methods found the same route!"
        else:
            fare_savings = total_fare - fare_cost
            distance_savings = total_distance - distance_cost
            analysis = f"💡 Comparison Analysis:\n"
            analysis += f"• Choosing cheapest route saves: ₱{fare_savings:.0f}\n"
            analysis += f"• Choosing shortest route saves: {distance_savings:.1f} km\n"
            if fare_savings > 0:
                analysis += f"• Fare difference per km saved: ₱{fare_savings/distance_savings:.1f}/km" if distance_savings > 0 else ""
        
        analysis_text = tk.Text(analysis_frame, height=3, wrap=tk.WORD, font=('Segoe UI', 9))
        analysis_text.insert(tk.END, analysis)
        analysis_text.config(state=tk.DISABLED)
        analysis_text.pack(fill=tk.X)
    
    def save_network_image(self):
        """Save the current network visualization as an image"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf"), ("SVG files", "*.svg"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.fig.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
                messagebox.showinfo("Export Successful", f"Network visualization saved to {filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to save image: {str(e)}")
    
    def import_data(self):
        """Import transportation data from CSV or JSON file"""
        filename = filedialog.askopenfilename(
            title="Import Transportation Data",
            filetypes=[("CSV files", "*.csv"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            if filename.lower().endswith('.json'):
                self.import_json_data(filename)
            else:
                self.import_csv_data(filename)
            
            # Refresh GUI after import
            self.refresh_after_data_change()
            messagebox.showinfo("Import Successful", f"Data imported successfully from {os.path.basename(filename)}")
            
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import data: {str(e)}")
    
    def import_csv_data(self, filename):
        """Import data from CSV file"""
        # Create new graph
        self.graph = TransportationGraph()
        
        with open(filename, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Handle different possible column names
                origin = row.get('Origin') or row.get('origin') or row.get('From') or row.get('from')
                destination = row.get('Destination') or row.get('destination') or row.get('To') or row.get('to')
                distance = float(row.get('Distance_km') or row.get('Distance (km)') or row.get('distance') or row.get('Distance'))
                fare = float(row.get('Fare_pesos') or row.get('Fare (₱)') or row.get('Fare (pesos)') or row.get('fare') or row.get('Fare'))
                
                self.graph.add_edge(origin, destination, distance, fare)
    
    def import_json_data(self, filename):
        """Import data from JSON file"""
        with open(filename, 'r') as file:
            data = json.load(file)
        
        # Create new graph
        self.graph = TransportationGraph()
        
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
            
            self.graph.add_edge(origin, destination, distance, fare)
    
    def export_data_csv(self):
        """Export current transportation data to CSV file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.graph.export_to_csv(filename)
                messagebox.showinfo("Export Successful", f"Data exported to {filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")
    
    def export_data_json(self):
        """Export current transportation data to JSON file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.export_to_json(filename)
                messagebox.showinfo("Export Successful", f"Data exported to {filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")
    
    def export_to_json(self, filename):
        """Export graph data to JSON format"""
        routes = []
        written_edges = set()
        
        for node in self.graph.nodes:
            for neighbor, distance, fare in self.graph.get_neighbors(node):
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
                'total_nodes': len(self.graph.nodes),
                'total_routes': len(routes),
                'export_timestamp': str(tk.datetime.datetime.now())
            },
            'routes': routes
        }
        
        with open(filename, 'w') as file:
            json.dump(data, file, indent=2)
    
    def reset_to_default(self):
        """Reset to default transportation network data"""
        result = messagebox.askyesno("Reset Data", 
                                   "This will reset all data to the default transportation network. Continue?")
        if result:
            self.graph = create_transportation_network()
            self.refresh_after_data_change()
            messagebox.showinfo("Reset Complete", "Data has been reset to default values.")
    
    def refresh_after_data_change(self):
        """Refresh GUI components after data change"""
        # Update combo box values
        node_list = sorted(list(self.graph.nodes))
        self.origin_combo['values'] = node_list
        self.destination_combo['values'] = node_list
        
        # Clear current results
        self.clear_results()
        
        # Refresh data table
        self.load_data_table()
        
        # Refresh visualization
        self.show_full_network()
    
    def show_all_routes_matrix(self):
        """Show a matrix of all possible routes"""
        matrix_window = tk.Toplevel(self.root)
        matrix_window.title("All Routes Matrix")
        matrix_window.geometry("1000x700")
        matrix_window.configure(bg='#f5f5f5')
        
        # Create main frame
        main_frame = ttk.Frame(matrix_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Complete Routes Matrix", 
                               font=('Segoe UI', 14, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Fare optimization tab
        fare_frame = ttk.Frame(notebook)
        notebook.add(fare_frame, text="💰 By Minimum Fare")
        self.create_routes_matrix_tab(fare_frame, 'fare')
        
        # Distance optimization tab
        distance_frame = ttk.Frame(notebook)
        notebook.add(distance_frame, text="📏 By Shortest Distance")
        self.create_routes_matrix_tab(distance_frame, 'distance')
    
    def create_routes_matrix_tab(self, parent, optimization):
        """Create a routes matrix tab for specific optimization"""
        # Create treeview
        tree_frame = ttk.Frame(parent, padding="10")
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('Origin', 'Destination', 'Path', 'Cost', 'Steps')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        
        # Configure columns
        tree.heading('Origin', text='From')
        tree.heading('Destination', text='To')
        tree.heading('Path', text='Route')
        tree.heading('Cost', text=f'Cost ({["₱", "km"][optimization == "distance"]})')
        tree.heading('Steps', text='Steps')
        
        tree.column('Origin', width=100)
        tree.column('Destination', width=100)
        tree.column('Path', width=400)
        tree.column('Cost', width=100)
        tree.column('Steps', width=80)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Populate with all possible routes
        nodes = sorted(list(self.graph.nodes))
        for origin in nodes:
            for destination in nodes:
                if origin != destination:
                    path, cost = self.graph.dijkstra(origin, destination, optimization)
                    if path:
                        tree.insert('', 'end', values=(
                            origin, destination, ' → '.join(path), 
                            f"{cost:.1f}", len(path) - 1
                        ))
    
    def show_about(self):
        """Show about dialog"""
        about_text = """Transportation Network Analysis Tool
        
Version: 2.0
Using: Dijkstra's Algorithm for Optimal Route Finding

Features:
• Find shortest and cheapest routes
• Interactive network visualization  
• Data import/export (CSV, JSON)
• Comprehensive route analysis
• Network statistics and efficiency metrics

Developed for transportation network optimization
using graph theory and algorithm analysis."""
        
        messagebox.showinfo("About Transportation Network Analysis", about_text)
    
    def show_user_guide(self):
        """Show user guide in a new window"""
        guide_window = tk.Toplevel(self.root)
        guide_window.title("User Guide")
        guide_window.geometry("700x500")
        guide_window.configure(bg='#f5f5f5')
        
        # Create scrollable text widget
        main_frame = ttk.Frame(guide_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        text_widget = tk.Text(main_frame, wrap=tk.WORD, font=('Segoe UI', 10))
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        guide_content = """USER GUIDE - Transportation Network Analysis Tool

BASIC USAGE:
1. Select your starting location (From) and destination (To)
2. Choose optimization method:
   • Minimum Fare: Find the cheapest route
   • Shortest Distance: Find the shortest physical route
3. Click "Find Route" to calculate optimal path
4. View results in the Route Results panel

FEATURES:

Route Planning:
• Use the ⇄ button to quickly swap origin/destination
• Compare Routes shows both optimization options side-by-side
• All Routes shows all possible routes from a selected origin

Data Management:
• Import Data: Load your own transportation data (CSV/JSON)
• Export Data: Save current network data
• Reset to Default: Restore original transportation network

Visualization:
• Network graph shows all locations and connections
• Red highlighting shows your selected route
• Save network image for presentations

Analysis Tools:
• Network Statistics: Comprehensive network analysis
• All Routes Matrix: Complete route combinations
• Data table shows efficiency metrics (fare per kilometer)

DATA FORMAT:
CSV files should have columns: Origin, Destination, Distance, Fare
JSON files should have routes array with origin, destination, distance, fare

KEYBOARD SHORTCUTS:
• Ctrl+O: Import data
• Ctrl+S: Export as CSV
• Ctrl+E: Export results
• Ctrl+Q: Exit application

TIPS:
• Use efficiency metrics to identify best value routes
• Compare different optimization methods for decision making
• Export results for documentation and reporting"""
        
        text_widget.insert(tk.END, guide_content)
        text_widget.config(state=tk.DISABLED)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                    
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