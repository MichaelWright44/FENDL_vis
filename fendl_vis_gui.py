#!/usr/bin/env python3
"""
Script to run the FENDL visualization GUI.
"""

import sys
import argparse
from pathlib import Path
from fendl_vis.gui import run_gui


def main():
    """Main function to run the FENDL GUI."""
    parser = argparse.ArgumentParser(description="FENDL Visualization GUI")
    parser.add_argument("--data-dir", default="data", help="Directory containing ENDF files")
    
    args = parser.parse_args()
    
    # Run the GUI with the specified data directory
    run_gui(data_dir=args.data_dir)


if __name__ == "__main__":
    main() 