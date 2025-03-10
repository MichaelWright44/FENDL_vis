"""
ENDF data plotting module.
"""

import matplotlib.pyplot as plt
import numpy as np


class EndfPlotter:
    """Class for plotting ENDF data."""
    
    @staticmethod
    def plot_cross_section(section_data, title=None, log_scale=True, show=True):
        """
        Plot cross section data from an ENDF file.
        
        Args:
            section_data (dict): Section data containing 'sigma' key with a Tabulated1D object
            title (str): Plot title
            log_scale (bool): Whether to use logarithmic scales
            show (bool): Whether to show the plot immediately
            
        Returns:
            tuple: (fig, ax) matplotlib figure and axes objects
        """
        # Check for required data
        if 'sigma' not in section_data:
            raise ValueError("Section data must contain 'sigma' key")
        
        # Get the data
        sigma = section_data['sigma']
        
        # If sigma is a Tabulated1D object, get its x and y values
        if hasattr(sigma, 'x') and hasattr(sigma, 'y'):
            x_data = sigma.x
            y_data = sigma.y
        # Otherwise, try to use E and sigma directly (fallback)
        elif 'E' in section_data and isinstance(section_data['sigma'], (list, np.ndarray)):
            x_data = section_data['E']
            y_data = section_data['sigma']
        else:
            raise ValueError("Could not find plottable cross section data. The 'sigma' key must be a Tabulated1D object or there must be 'E' and 'sigma' arrays.")
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Plot the data
        if log_scale:
            ax.loglog(x_data, y_data, '-', lw=2, marker='.', markersize=4)
            ax.grid(True, which='both', linestyle='--', alpha=0.7)
        else:
            ax.plot(x_data, y_data, '-', lw=2, marker='.', markersize=4)
            ax.grid(True, linestyle='--', alpha=0.7)
        
        # Set labels
        ax.set_xlabel('Energy (eV)')
        ax.set_ylabel('Cross Section (barns)')
        
        # Set title
        if title:
            ax.set_title(title)
        
        # Show if requested
        if show:
            plt.tight_layout()
            plt.show()
        
        return fig, ax
    
    @staticmethod
    def plot_multiple_cross_sections(material, mt_list, title=None, log_scale=True, show=True):
        """
        Plot multiple cross sections on the same graph.
        
        Args:
            material (endf.Material): The ENDF material
            mt_list (list): List of MT numbers to plot
            title (str): Plot title
            log_scale (bool): Whether to use logarithmic scales
            show (bool): Whether to show the plot immediately
            
        Returns:
            tuple: (fig, ax) matplotlib figure and axes objects
        """
        # Create the plot
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Plot each cross section
        for mt in mt_list:
            if (3, mt) in material.section_data:
                section = material.section_data[3, mt]
                if 'sigma' in section:
                    sigma = section['sigma']
                    
                    # Get MT description
                    mt_desc = EndfPlotter._get_mt_description(mt)
                    
                    # If sigma is a Tabulated1D object, get its x and y values
                    if hasattr(sigma, 'x') and hasattr(sigma, 'y'):
                        if log_scale:
                            ax.loglog(sigma.x, sigma.y, '-', lw=2, label=f"MT={mt} ({mt_desc})")
                        else:
                            ax.plot(sigma.x, sigma.y, '-', lw=2, label=f"MT={mt} ({mt_desc})")
        
        # Set labels and title
        ax.set_xlabel('Energy (eV)')
        ax.set_ylabel('Cross Section (barns)')
        
        if title:
            ax.set_title(title)
        else:
            ax.set_title(f"Cross Sections Comparison")
        
        # Add legend and grid
        ax.legend()
        ax.grid(True, which='both' if log_scale else 'major', linestyle='--', alpha=0.7)
        
        # Show if requested
        if show:
            plt.tight_layout()
            plt.show()
        
        return fig, ax
    
    @staticmethod
    def plot_general_data(x_data, y_data, title=None, xlabel=None, ylabel=None, 
                          log_scale=True, show=True):
        """
        General purpose plotting function for any x,y data.
        
        Args:
            x_data (array): X-axis data
            y_data (array): Y-axis data
            title (str): Plot title
            xlabel (str): X-axis label
            ylabel (str): Y-axis label
            log_scale (bool): Whether to use logarithmic scales
            show (bool): Whether to show the plot immediately
            
        Returns:
            tuple: (fig, ax) matplotlib figure and axes objects
        """
        # Create the plot
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Plot the data
        if log_scale:
            ax.loglog(x_data, y_data, '-', lw=2, marker='.', markersize=4)
            ax.grid(True, which='both', linestyle='--', alpha=0.7)
        else:
            ax.plot(x_data, y_data, '-', lw=2, marker='.', markersize=4)
            ax.grid(True, linestyle='--', alpha=0.7)
        
        # Set labels
        if xlabel:
            ax.set_xlabel(xlabel)
        if ylabel:
            ax.set_ylabel(ylabel)
        
        # Set title
        if title:
            ax.set_title(title)
        
        # Show if requested
        if show:
            plt.tight_layout()
            plt.show()
        
        return fig, ax
    
    @staticmethod
    def close_plots():
        """Close all open matplotlib plots."""
        plt.close('all')
    
    @staticmethod
    def _get_mt_description(mt):
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