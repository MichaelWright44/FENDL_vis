"""
ENDF file viewer module.
"""

import json
import numpy as np


class EndfViewer:
    """Class for displaying ENDF data."""
    
    @staticmethod
    def display_evaluation_info(material):
        """
        Display basic information about an ENDF material.
        
        Args:
            material (endf.Material): The ENDF material.
        """
        print("\n== ENDF File Information ==")
        
        # Display basic material properties
        if hasattr(material, 'MAT'):
            print(f"MAT: {material.MAT}")
        if hasattr(material, 'ZA'):
            print(f"ZA: {material.ZA}")
        if hasattr(material, 'AWR'):
            print(f"AWR: {material.AWR}")
            
        # Get information from MF=1, MT=451 if available
        if (1, 451) in material.section_data:
            header = material.section_data[1, 451]
            print("\nHeader Information (MF=1, MT=451):")
            for key in ['ZA', 'AWR', 'TEMP', 'LREL', 'date']:
                if key in header:
                    print(f"  {key}: {header[key]}")
        
        # Get interpreted data if possible
        try:
            interpreted_data = material.interpret()
            print(f"\nInterpreted as: {type(interpreted_data).__name__}")
            
            # Add specific information for incident neutron data
            if hasattr(interpreted_data, 'reactions'):
                print("\nAvailable Reactions:")
                for mt, reaction in sorted(interpreted_data.reactions.items()):
                    print(f"  MT={mt}: {str(reaction)}")
        except Exception as e:
            print(f"\nCould not interpret material: {e}")
            
        # Display available sections
        print("\nAvailable Sections:")
        for (mf, mt) in sorted(material.section_data.keys()):
            desc = EndfViewer._get_section_description(mf, mt)
            print(f"  MF={mf}, MT={mt}: {desc}")
    
    @staticmethod
    def display_section(material, mf, mt):
        """
        Display information about a specific section of an ENDF file.
        
        Args:
            material (endf.Material): The ENDF material.
            mf (int): The MF (file) number.
            mt (int): The MT (section) number.
        """
        # Check if the section exists
        if (mf, mt) not in material.section_data:
            print(f"Section (MF={mf}, MT={mt}) not found in material.")
            return
        
        section = material.section_data[mf, mt]
        print(f"\n== Section MF={mf}, MT={mt} ==")
        print(f"Description: {EndfViewer._get_section_description(mf, mt)}")
        
        # Display section content based on MF number
        if mf == 1 and mt == 451:
            # File info and dictionary
            EndfViewer._display_file_info(section)
        elif mf == 3:
            # Cross sections
            EndfViewer._display_cross_section(section)
        else:
            # Generic section data display
            EndfViewer._display_generic_section(section)
    
    @staticmethod
    def _display_file_info(section):
        """Display file information from MF=1, MT=451 section."""
        print("\nFile Information:")
        for key, value in section.items():
            if isinstance(value, (int, float, str)):
                print(f"  {key}: {value}")
    
    @staticmethod
    def _display_cross_section(section):
        """Display cross section data from MF=3 section."""
        # Check for essential fields
        essential_fields = ['E', 'sigma']
        if not all(field in section for field in essential_fields):
            print("Cross section data not found in section.")
            return
        
        E = section['E']
        sigma = section['sigma']
        
        # Display some metadata if available
        if 'QM' in section:
            print(f"\nQ-value: {section['QM']} eV")
        if 'threshold_idx' in section:
            threshold_idx = section['threshold_idx']
            if threshold_idx < len(E):
                print(f"Threshold Energy: {E[threshold_idx]:.6e} eV")
        
        # Display a sample of the cross section data
        points = min(10, len(E))
        print(f"\nCross Section Data (showing {points} of {len(E)} points):")
        print("  Energy (eV)    Cross Section (barns)")
        print("  -----------    --------------------")
        
        # Determine which points to show (first, middle, and last)
        if points >= 3:
            indices = [0]  # First point
            # Some points in the middle
            middle_count = points - 2
            if middle_count > 0:
                step = max(1, (len(E) - 2) // middle_count)
                indices.extend(range(1, len(E) - 1, step)[:middle_count])
            indices.append(len(E) - 1)  # Last point
        else:
            indices = list(range(min(points, len(E))))
        
        # Display the selected points
        for i in indices:
            print(f"  {E[i]:.6e}    {sigma[i]:.6e}")
    
    @staticmethod
    def _display_generic_section(section):
        """Display generic section data."""
        # For dictionary-like sections
        if isinstance(section, dict):
            # First display scalar values
            scalars = {k: v for k, v in section.items() if isinstance(v, (int, float, str))}
            if scalars:
                print("\nSection Properties:")
                for key, value in sorted(scalars.items()):
                    print(f"  {key}: {value}")
            
            # Then display arrays (just their sizes)
            arrays = {k: v for k, v in section.items() if isinstance(v, (list, np.ndarray))}
            if arrays:
                print("\nData Arrays:")
                for key, value in sorted(arrays.items()):
                    size = len(value) if hasattr(value, '__len__') else "unknown"
                    print(f"  {key}: {size} elements")
        else:
            # For other types of sections
            print(f"\nSection content (type: {type(section).__name__}):")
            print(str(section)[:1000] + "..." if len(str(section)) > 1000 else str(section))
    
    @staticmethod
    def display_as_json(data, indent=2):
        """
        Display data in pretty JSON format.
        
        Args:
            data: Data to display.
            indent (int): Indentation for JSON formatting.
        """
        print(json.dumps(data, indent=indent, default=str))
    
    @staticmethod
    def _get_section_description(mf, mt):
        """
        Get a description for an ENDF section.
        
        Args:
            mf (int): The MF (file) number.
            mt (int): The MT (section) number.
            
        Returns:
            str: A description of the section.
        """
        # Special case for file info section
        if mf == 1 and mt == 451:
            return "General information and section directory"
        
        # First get the MF description
        mf_desc = EndfViewer._get_mf_description(mf)
        
        # Then get the MT description
        mt_desc = EndfViewer._get_mt_description(mt)
        
        return f"{mf_desc} - {mt_desc}"
    
    @staticmethod
    def _get_mf_description(mf):
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