# FENDL data processing and visualization Library

A Python library for loading, parsing, and visualizing ENDF data from the FENDL (Fusion Evaluated Nuclear Data Library).

## Installation

```bash
pip install -e .
```
## Requirements

- Python 3.6+
- endf>=0.1.0
- matplotlib>=3.5.0
- numpy>=1.20.0
- tkinter (usually comes with Python)

## Usage

### Graphical User Interface (GUI)

The library includes a simple GUI for browsing and plotting ENDF data:

```bash
# Run the GUI with default data directory
python fendl_vis_gui.py

# Specify a different data directory
python fendl_vis_gui.py --data-dir /path/to/endf/files
```

In the GUI, you can:
1. Browse and select ENDF files
2. Choose sections (MF, MT) to view
3. Toggle logarithmic/linear scales
4. Compare multiple cross sections (with the "Compare Common Cross Sections" option)
5. View and interact with plots using the matplotlib navigation toolbar
6. View formatted text data for sections without plottable data (like MF=1 General Information)

#### Example: Cross Section Plot View
![Cross Section Plot View](docs/data_plotting.png)

#### Example: Text Data View
![Text Data View](docs/metadata_info.png)

### Python API

You can also use the library programmatically:

```python
from fendl_vis import EndfLoader, EndfViewer, EndfPlotter
import matplotlib.pyplot as plt

# Initialize the loader
loader = EndfLoader('data')

# List available files
endf_files = loader.list_files()
for file in endf_files:
    print(file)

# Load a file
material = loader.load_file('data/n_0125_1-H-1.endf')

# Display basic information
EndfViewer.display_evaluation_info(material)

# Get section data for plotting (MF=3, MT=1 is total cross section)
if (3, 1) in material.section_data:
    section = material.section_data[3, 1]
    
    # Create a plot of the cross section
    fig, ax = EndfPlotter.plot_cross_section(section, title="Total Cross Section")
    plt.show()
    
    # Plot multiple cross sections for comparison
    common_mt = [1, 2, 102]  # Total, elastic, capture
    fig, ax = EndfPlotter.plot_multiple_cross_sections(
        material, common_mt, title="Cross Section Comparison"
    )
    plt.show()

# Get information as a dictionary
info = loader.get_evaluation_info(material)
print(info)
```

## ENDF Data Structure

ENDF (Evaluated Nuclear Data File) format organizes data into:

- **MF** (File numbers): Represent different types of data
  - MF=1: General information
  - MF=3: Cross section data
  - MF=4: Angular distributions
  - etc.

- **MT** (Section numbers): Represent different reactions
  - MT=1: Total cross section
  - MT=2: Elastic scattering
  - MT=102: Radiative capture
  - etc.

## Features

- Load and parse ENDF files from FENDL
- Simple GUI for interactive browsing and plotting
- Plot cross sections and other data
- Compare multiple cross sections in a single plot
- Display structured text data for non-plottable sections
- Display information about ENDF materials
- Explore specific sections (MF, MT) within the files
- Support for both logarithmic and linear scales
- Interactive matplotlib plots with zoom, pan, and save capabilities
- Proper handling of Tabulated1D objects from the ENDF library

## Development

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License
