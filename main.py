"""
Transportation Network Analysis - Main Application Entry Point
Transportation Project using Dijkstra's Algorithm
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
import logging

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from gui_interface import TransportationGUI, NetworkAnalysisWindow
    from graph_data import create_transportation_network
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all required files are in the same directory.")
    sys.exit(1)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('transportation_app.log'),
        logging.StreamHandler()
    ]
)

class TransportationApp:
    """Main application class"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Starting Transportation Network Application")

    def check_dependencies(self):
        """Check if all required dependencies are installed"""
        required_packages = [
            'tkinter', 'matplotlib', 'networkx', 'pandas', 'numpy'
        ]

        missing_packages = []

        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)

        if missing_packages:
            error_msg = f"Missing required packages: {', '.join(missing_packages)}\n"
            error_msg += "Please install them using: pip install " + " ".join(missing_packages)
            self.logger.error(error_msg)

            # Show error dialog if tkinter is available
            if 'tkinter' not in missing_packages:
                root = tk.Tk()
                root.withdraw()
                messagebox.showerror("Missing Dependencies", error_msg)
                root.destroy()
            else:
                print(error_msg)

            return False

        return True

    def run(self):
        """Run the main application"""
        try:
            # Check dependencies
            if not self.check_dependencies():
                return False

            # Create and run the GUI
            app = TransportationGUI()
            self.logger.info("GUI application started successfully")

            # Add exception handling for the GUI
            app.root.report_callback_exception = self.handle_exception

            app.run()

            self.logger.info("Application closed successfully")
            return True

        except Exception as e:
            self.logger.error(f"Application error: {str(e)}", exc_info=True)

            # Try to show error dialog
            try:
                root = tk.Tk()
                root.withdraw()
                messagebox.showerror("Application Error",
                                   f"An unexpected error occurred:\n{str(e)}\n\nCheck the log file for details.")
                root.destroy()
            except:
                print(f"Critical error: {str(e)}")

            return False

    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """Handle uncaught exceptions in the GUI"""
        error_msg = f"Uncaught exception: {exc_type.__name__}: {exc_value}"
        self.logger.error(error_msg, exc_info=(exc_type, exc_value, exc_traceback))

        # Show error dialog
        messagebox.showerror("Application Error",
                           f"An error occurred:\n{error_msg}\n\nCheck the log file for details.")


def test_dijkstra_algorithm():
    """Test the Dijkstra algorithm implementation"""
    print("Testing Dijkstra's Algorithm Implementation...")
    print("=" * 50)

    # Create the transportation network
    graph = create_transportation_network()

    # Test cases
    test_cases = [
        ("Tagoloan", "Indahag", "fare"),
        ("Tagoloan", "Indahag", "distance"),
        ("Gusa", "Taguanao", "fare"),
        ("Balulang", "Iponan", "distance"),
        ("Carmen", "Pagatpat", "fare")
    ]

    for origin, destination, optimization in test_cases:
        print(f"\nTest: {origin} → {destination} (optimize for {optimization})")
        path, cost = graph.dijkstra(origin, destination, optimization)

        if path:
            print(f"Path: {' → '.join(path)}")
            print(f"Cost: {cost:.1f} {'pesos' if optimization == 'fare' else 'km'}")

            # Show detailed route
            details = graph.get_route_details(path)
            print("Route details:")
            for i, detail in enumerate(details, 1):
                print(f"  {i}. {detail['from']} → {detail['to']}: "
                      f"{detail['distance']:.1f} km, ₱{detail['fare']:.0f}")
        else:
            print("No path found!")

    print("\n" + "=" * 50)
    print("Testing completed successfully!")


def create_sample_data_file():
    """Create a sample CSV file with transportation data"""
    filename = "transportation_data.csv"

    try:
        graph = create_transportation_network()
        graph.export_to_csv(filename)
        print(f"Sample data file created: {filename}")
        return True
    except Exception as e:
        print(f"Error creating sample data file: {e}")
        return False


def show_help():
    """Show help information"""
    help_text = """

Transportation Network Analysis - Help
=====================================

This application implements Dijkstra's algorithm to find optimal routes
in a transportation network.

Usage:
    python main.py              - Start the GUI application
    python main.py --test       - Test the algorithm
    python main.py --help       - Show this help
    python main.py --create-data - Create sample data file

Locations in the network:
- Tagoloan, Gusa, Balulang, Carmen
- Pagatpat, Iponan, Indahag, Taguanao

For more information, see the README.md file.
"""
    print(help_text)


def main():
    """Main entry point"""
    # Parse command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()

        if arg in ['--help', '-h']:
            show_help()
            return
        elif arg == '--test':
            test_dijkstra_algorithm()
            return
        elif arg == '--create-data':
            create_sample_data_file()
            return
        else:
            print(f"Unknown argument: {arg}")
            print("Use --help for usage information")
            return

    # Run the main application
    app = TransportationApp()
    success = app.run()

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
