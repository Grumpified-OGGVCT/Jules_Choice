"""
Data Visualization App

This application reads a JSON file of key-value pairs and generates a bar chart
using matplotlib, saving it to chart.png.
"""

import argparse
import json
import matplotlib.pyplot as plt
import os

def generate_chart(data_path: str, output_path: str) -> None:
    """Generate a bar chart from the provided JSON data."""
    if not os.path.exists(data_path):
        print(f"Error: Data file {data_path} not found.")
        return

    try:
        with open(data_path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON data: {e}")
        return

    if not isinstance(data, dict):
        print("Error: JSON data must be a dictionary of key-value pairs.")
        return

    keys = list(data.keys())
    values = list(data.values())

    plt.figure(figsize=(10, 6))
    plt.bar(keys, values, color='skyblue')
    plt.xlabel('Categories')
    plt.ylabel('Values')
    plt.title('Autonomous AI Agent Metrics')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    plt.savefig(output_path)
    print(f"Chart successfully saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a bar chart from JSON data.")
    parser.add_argument("--data", type=str, default="data.json", help="Path to input JSON file")
    parser.add_argument("--output", type=str, default="chart.png", help="Path to output PNG file")
    args = parser.parse_args()

    # If default data.json doesn't exist, create a mock one
    if args.data == "data.json" and not os.path.exists("data.json"):
        mock_data = {
            "Scribe Commits": 42,
            "Sentinel Scans": 15,
            "Oracle Queries": 89,
            "Weaver Integrations": 23,
            "CoVE Test Passes": 104
        }
        with open("data.json", "w") as f:
            f.write(json.dumps(mock_data, indent=2))
        print("Created mock data.json")

    generate_chart(args.data, args.output)
