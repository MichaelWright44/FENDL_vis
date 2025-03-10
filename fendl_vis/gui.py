"""
Simple GUI for browsing and plotting ENDF data.
"""

import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from .loader import EndfLoader
from .plotter import EndfPlotter


class EndfGui:
    """Simple GUI for browsing and plotting ENDF data."""
    
    def __init__(self, root, data_dir="data"):
        """Initialize the GUI."""
        self.root = root
        self.root.title("FENDL Visualization Tool")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        self.data_dir = Path(data_dir)
        self.loader = EndfLoader(self.data_dir)
        self.material = None
        self.current_plot = None
        
        self._create_widgets()
        self._load_file_list()
    
    def _create_widgets(self):
        """Create the GUI widgets."""
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create left panel (file selection, section selection)
        self.left_panel = ttk.Frame(self.main_frame, padding="5", width=300)
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y, expand=False)
        
        # Create right panel (plot area)
        self.right_panel = ttk.Frame(self.main_frame, padding="5")
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # File selection widgets
        self.file_frame = ttk.LabelFrame(self.left_panel, text="ENDF File Selection", padding="5")
        self.file_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Create file list
        self.file_list = tk.Listbox(self.file_frame, width=40, height=10)
        self.file_list.pack(fill=tk.X, padx=5, pady=5)
        self.file_list.bind('<<ListboxSelect>>', self._on_file_select)
        
        # Browse button
        self.browse_button = ttk.Button(self.file_frame, text="Browse...", command=self._browse_file)
        self.browse_button.pack(fill=tk.X, padx=5, pady=5)
        
        # Section selection widgets
        self.section_frame = ttk.LabelFrame(self.left_panel, text="Section Selection", padding="5")
        self.section_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # MF selection
        ttk.Label(self.section_frame, text="MF (File Number):").pack(anchor=tk.W, padx=5, pady=2)
        self.mf_combo = ttk.Combobox(self.section_frame, state="readonly")
        self.mf_combo.pack(fill=tk.X, padx=5, pady=5)
        self.mf_combo.bind("<<ComboboxSelected>>", self._on_mf_select)
        
        # MT selection
        ttk.Label(self.section_frame, text="MT (Section Number):").pack(anchor=tk.W, padx=5, pady=2)
        self.mt_combo = ttk.Combobox(self.section_frame, state="readonly")
        self.mt_combo.pack(fill=tk.X, padx=5, pady=5)
        
        # Plot options
        self.options_frame = ttk.LabelFrame(self.left_panel, text="Plot Options", padding="5")
        self.options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Log scale checkbox
        self.log_scale_var = tk.BooleanVar(value=True)
        self.log_scale_check = ttk.Checkbutton(
            self.options_frame, 
            text="Logarithmic Scale", 
            variable=self.log_scale_var
        )
        self.log_scale_check.pack(anchor=tk.W, padx=5, pady=5)
        
        # Compare checkbox (for multiple cross sections)
        self.compare_var = tk.BooleanVar(value=False)
        self.compare_check = ttk.Checkbutton(
            self.options_frame,
            text="Compare Common Cross Sections",
            variable=self.compare_var
        )
        self.compare_check.pack(anchor=tk.W, padx=5, pady=5)
        
        # Plot button
        self.plot_button = ttk.Button(
            self.left_panel, 
            text="Plot Selected Section", 
            command=self._plot_section,
            state=tk.DISABLED
        )
        self.plot_button.pack(fill=tk.X, padx=5, pady=10)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(
            self.root, 
            textvariable=self.status_var, 
            relief=tk.SUNKEN, 
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Plot area
        self.plot_frame = ttk.Frame(self.right_panel)
        self.plot_frame.pack(fill=tk.BOTH, expand=True)
        
        # Initial figure
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.ax.set_xlabel('Energy (eV)')
        self.ax.set_ylabel('Cross Section (barns)')
        self.ax.text(0.5, 0.5, 'Select a file and section to plot', 
                      ha='center', va='center', transform=self.ax.transAxes)
        self.ax.grid(True)
        
        # Canvas for the plot
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Navigation toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame)
        self.toolbar.update()
    
    def _load_file_list(self):
        """Load the list of ENDF files from the data directory."""
        try:
            self.endf_files = self.loader.list_files()
            self.file_list.delete(0, tk.END)
            for i, file in enumerate(self.endf_files):
                self.file_list.insert(i, file.name)
            
            if self.endf_files:
                self.status_var.set(f"Found {len(self.endf_files)} ENDF files in {self.data_dir}")
            else:
                self.status_var.set(f"No ENDF files found in {self.data_dir}")
        except Exception as e:
            messagebox.showerror("Error", f"Error loading file list: {e}")
            self.status_var.set("Error loading file list")
    
    def _browse_file(self):
        """Browse for an ENDF file."""
        filename = filedialog.askopenfilename(
            title="Select ENDF File",
            filetypes=[("ENDF Files", "*.endf"), ("All Files", "*.*")]
        )
        
        if filename:
            try:
                self.data_dir = Path(filename).parent
                self.loader = EndfLoader(self.data_dir)
                self._load_file_list()
                
                # Select the browsed file
                for i, file in enumerate(self.endf_files):
                    if file.name == Path(filename).name:
                        self.file_list.selection_clear(0, tk.END)
                        self.file_list.selection_set(i)
                        self.file_list.see(i)
                        self._on_file_select(None)
                        break
            except Exception as e:
                messagebox.showerror("Error", f"Error loading file: {e}")
    
    def _on_file_select(self, event):
        """Handle file selection."""
        selection = self.file_list.curselection()
        if not selection:
            return
        
        index = selection[0]
        selected_file = self.endf_files[index]
        
        try:
            self.status_var.set(f"Loading {selected_file.name}...")
            self.root.update_idletasks()  # Force update to show status
            
            self.material = self.loader.load_file(selected_file)
            self._update_section_combos()
            self.status_var.set(f"Loaded {selected_file.name}")
            self.plot_button.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Error", f"Error loading file: {e}")
            self.status_var.set(f"Error loading {selected_file.name}")
    
    def _update_section_combos(self):
        """Update the MF and MT comboboxes based on the loaded material."""
        if not self.material:
            return
        
        # Get unique MF values
        mf_values = sorted(set(mf for mf, mt in self.material.section_data.keys()))
        mf_labels = [f"{mf}: {self._get_mf_description(mf)}" for mf in mf_values]
        
        self.mf_combo['values'] = mf_labels
        self.mf_combo.current(0)  # Select first MF
        
        # Update MT values for selected MF
        self._on_mf_select(None)
    
    def _on_mf_select(self, event):
        """Handle MF selection."""
        if not self.material or not self.mf_combo.get():
            return
        
        # Get the selected MF value
        selected_mf = int(self.mf_combo.get().split(':')[0])
        
        # Get all MT values for the selected MF
        mt_values = sorted(mt for mf, mt in self.material.section_data.keys() if mf == selected_mf)
        mt_labels = [f"{mt}: {self._get_mt_description(mt)}" for mt in mt_values]
        
        self.mt_combo['values'] = mt_labels
        self.mt_combo.current(0)  # Select first MT
    
    def _plot_section(self):
        """Plot the selected section."""
        if not self.material:
            return
        
        try:
            # Check if compare mode is enabled
            if self.compare_var.get():
                self._plot_comparison()
                return
            
            # Get selected MF and MT
            selected_mf = int(self.mf_combo.get().split(':')[0])
            selected_mt = int(self.mt_combo.get().split(':')[0])
            
            # Get the section data
            if (selected_mf, selected_mt) not in self.material.section_data:
                messagebox.showerror("Error", f"Section (MF={selected_mf}, MT={selected_mt}) not found")
                return
            
            section_data = self.material.section_data[selected_mf, selected_mt]
            
            # Clear previous plot
            if hasattr(self, 'canvas'):
                self.canvas.get_tk_widget().destroy()
            if hasattr(self, 'toolbar'):
                self.toolbar.destroy()
            
            # Close previous plot
            plt.close(self.fig)
            
            # Create title
            title = f"MF={selected_mf} ({self._get_mf_description(selected_mf)}), " \
                    f"MT={selected_mt} ({self._get_mt_description(selected_mt)})"
            
            # Create a new plot
            if selected_mf == 3 and 'sigma' in section_data:
                try:
                    # Try to plot cross section data
                    self.fig, self.ax = EndfPlotter.plot_cross_section(
                        section_data,
                        title=title,
                        log_scale=self.log_scale_var.get(),
                        show=False
                    )
                    self.status_var.set(f"Plotted cross section (MF={selected_mf}, MT={selected_mt})")
                except Exception as e:
                    # If that fails, fall back to generic plot
                    self._plot_generic_data(section_data, title)
            else:
                # For non-cross-section data, try to find plottable data
                self._plot_generic_data(section_data, title)
            
            # Add the plot to the GUI
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Add toolbar
            self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame)
            self.toolbar.update()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error plotting section: {e}")
            self.status_var.set("Error plotting section")
    
    def _plot_generic_data(self, section_data, title):
        """Try to plot generic data from a section."""
        # Try to find plottable data
        x_data = None
        y_data = None
        xlabel = None
        ylabel = None
        
        # Look for Tabulated1D objects first
        for key in section_data:
            if hasattr(section_data[key], 'x') and hasattr(section_data[key], 'y'):
                x_data = section_data[key].x
                y_data = section_data[key].y
                xlabel = 'X values'
                ylabel = f'{key} values'
                break
        
        # If no Tabulated1D found, look for common arrays
        if x_data is None:
            for x_key in ['E', 'energy', 'x']:
                if x_key in section_data and isinstance(section_data[x_key], (list, np.ndarray)):
                    x_data = section_data[x_key]
                    xlabel = 'Energy (eV)' if x_key in ['E', 'energy'] else 'X values'
                    break
            
            for y_key in ['sigma', 'data', 'y']:
                if y_key in section_data and isinstance(section_data[y_key], (list, np.ndarray)):
                    y_data = section_data[y_key]
                    ylabel = 'Cross Section (barns)' if y_key == 'sigma' else 'Y values'
                    break
        
        if x_data is not None and y_data is not None and len(x_data) == len(y_data):
            # Plot the data
            self.fig, self.ax = EndfPlotter.plot_general_data(
                x_data, y_data,
                title=title,
                xlabel=xlabel,
                ylabel=ylabel,
                log_scale=self.log_scale_var.get(),
                show=False
            )
            self.status_var.set(f"Plotted generic data")
        else:
            # Create an empty plot with message
            self.fig, self.ax = plt.subplots(figsize=(6, 4))
            self.ax.text(0.5, 0.5, 'No plottable data found in this section',
                        ha='center', va='center', transform=self.ax.transAxes)
            self.ax.set_title(title)
            self.status_var.set("No plottable data found")
    
    def _plot_comparison(self):
        """Plot comparison of common cross sections."""
        if not self.material:
            return
        
        try:
            # Common important cross sections to compare
            common_mt = [1, 2, 102]  # Total, elastic, capture
            
            # Add any others that are available in the material
            for mt in [16, 18, 103, 104, 105]:  # n,2n - fission - n,p - n,d - n,t
                if (3, mt) in self.material.section_data:
                    common_mt.append(mt)
            
            # Clear previous plot
            if hasattr(self, 'canvas'):
                self.canvas.get_tk_widget().destroy()
            if hasattr(self, 'toolbar'):
                self.toolbar.destroy()
            
            # Close previous plot
            plt.close(self.fig)
            
            # Create a new multi-plot
            self.fig, self.ax = EndfPlotter.plot_multiple_cross_sections(
                self.material,
                common_mt,
                title=f"Cross Section Comparison",
                log_scale=self.log_scale_var.get(),
                show=False
            )
            
            # Add the plot to the GUI
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Add toolbar
            self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame)
            self.toolbar.update()
            
            self.status_var.set(f"Plotted comparison of common cross sections")
        except Exception as e:
            messagebox.showerror("Error", f"Error plotting comparison: {e}")
            self.status_var.set("Error plotting comparison")
    
    def _get_mf_description(self, mf):
        """Get description for an MF number."""
        mf_descriptions = {
            1: "General Information",
            2: "Resonance Parameters",
            3: "Cross Sections",
            4: "Angular Distributions",
            5: "Energy Distributions",
            6: "Energy-Angle Distributions",
            7: "Thermal Scattering Data",
            8: "Radioactivity and Fission-Product Yields",
            9: "Multiplicities",
            10: "Cross Sections for Production of Radioactive Nuclides",
            12: "Multiplicities and Transition Probability Arrays",
            13: "Photon Production Cross Sections",
            14: "Photon Angular Distributions",
            15: "Continuous Photon Energy Spectra",
            23: "Smooth Photon Interaction Cross Sections",
            27: "Atomic Form Factors"
        }
        return mf_descriptions.get(mf, f"File {mf}")
    
    def _get_mt_description(self, mt):
        """Get description for an MT number."""
        mt_descriptions = {
            1: "Total cross section",
            2: "Elastic scattering",
            3: "Nonelastic cross section",
            4: "Inelastic cross section",
            5: "Sum of all reactions not given explicitly",
            16: "(n,2n)",
            17: "(n,3n)",
            18: "Fission",
            51: "Inelastic scattering to 1st excited state",
            102: "Radiative capture (n,gamma)",
            103: "(n,p)",
            104: "(n,d)",
            105: "(n,t)",
            451: "File information and dictionary"
        }
        return mt_descriptions.get(mt, f"MT={mt}")


def run_gui(data_dir="data"):
    """Run the ENDF GUI application."""
    root = tk.Tk()
    app = EndfGui(root, data_dir)
    root.mainloop() 