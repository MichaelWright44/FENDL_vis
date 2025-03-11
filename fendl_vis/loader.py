"""
ENDF file loader module.
"""

from pathlib import Path
import endf


class EndfLoader:
    """Class for loading and parsing ENDF files."""
    
    def __init__(self, data_dir="data"):
        """
        Initialize the ENDF loader.
        
        Args:
            data_dir (str): Path to the directory containing ENDF files.
        """
        self.data_dir = Path(data_dir)
        if not self.data_dir.exists() or not self.data_dir.is_dir():
            raise ValueError(f"Directory '{data_dir}' not found or is not a directory.")
    
    def list_files(self):
        """
        List all ENDF files in the data directory.
        
        Returns:
            list: List of Path objects for each ENDF file.
        """
        return sorted(self.data_dir.glob("*.endf"))
    
    def load_file(self, file_path):
        """
        Load and parse an ENDF file.
        
        Args:
            file_path (str or Path): Path to the ENDF file.
            
        Returns:
            endf.Material: The parsed ENDF material.
            
        Raises:
            FileNotFoundError: If the file does not exist.
            Exception: If there is an error parsing the file.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File '{file_path}' not found.")
        
        try:
            # Use the Material class to parse the file
            material = endf.Material(str(file_path))
            return material
        except Exception as e:
            raise Exception(f"Error parsing ENDF file: {e}")
    
    def get_high_level_data(self, material):
        """
        Get high-level data from the ENDF material by interpreting it.
        
        Args:
            material (endf.Material): The ENDF material.
            
        Returns:
            object: The interpreted data (like IncidentNeutron)
        """
        try:
            interpreted_data = material.interpret()
            return interpreted_data
        except Exception as e:
            print(f"Warning: Could not interpret material: {e}")
            return None
    
    def get_evaluation_info(self, material):
        """
        Extract basic information from an ENDF material.
        
        Args:
            material (endf.Material): The ENDF material.
            
        Returns:
            dict: Dictionary containing basic information about the material.
        """
        info = {"sections": []}
        
        # Add basic material info
        for attr in ['MAT', 'ZA', 'AWR']:
            if hasattr(material, attr):
                info[attr] = getattr(material, attr)
        
        # Get metadata from MF=1, MT=451 if available
        if (1, 451) in material.section_data:
            header = material.section_data[1, 451]
            for key in ['ZA', 'AWR', 'LREL', 'LRP', 'TEMP']:
                if key in header:
                    info[key] = header[key]
        
        # Add information about available sections
        for (mf, mt) in sorted(material.section_data.keys()):
            section_info = {
                "mf": mf,
                "mt": mt,
                "description": self._get_section_description(mf, mt)
            }
            info["sections"].append(section_info)
        
        # Try to get high-level data
        interpreted = self.get_high_level_data(material)
        if interpreted is not None:
            info["interpreted_type"] = type(interpreted).__name__
            
            # If it's incident neutron data, add reaction info
            if hasattr(interpreted, 'reactions'):
                info["reactions"] = []
                for mt, reaction in interpreted.reactions.items():
                    reaction_info = {
                        "mt": mt,
                        "name": str(reaction)
                    }
                    info["reactions"].append(reaction_info)
        
        return info
    
    def _get_section_description(self, mf, mt):
        """
        Get description for an MF, MT section.
        
        Args:
            mf (int): The MF (file) number.
            mt (int): The MT (section) number.
            
        Returns:
            str: Description of the section.
        """
        # Special case for file info section
        if mf == 1 and mt == 451:
            return "General information"
        
        # First get the MF description
        mf_desc = self._get_mf_description(mf)
        
        # Then get the MT description
        mt_desc = self._get_mt_description(mt)
        
        return f"{mf_desc} - {mt_desc}"
    
    def _get_mf_description(self, mf):
        """
        Get description for an MF number.
        
        Args:
            mf (int): The MF number.
            
        Returns:
            str: Description of the MF file.
        """
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
        """
        Get description for an MT number.
        
        Args:
            mt (int): The MT number.
            
        Returns:
            str: Description of the MT reaction.
        """
        # Common MT numbers and their descriptions
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