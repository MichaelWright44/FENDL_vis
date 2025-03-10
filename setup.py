from setuptools import setup, find_packages

setup(
    name="fendl_vis",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "endf>=0.1.0",
        "matplotlib>=3.5.0",
        "numpy>=1.20.0",
    ],
    entry_points={
        'console_scripts': [
            'fendl-vis=fendl_vis.cli:main',
        ],
    },
    description="Library for loading and visualizing ENDF data from FENDL",
    author="FENDL Developer",
    author_email="example@example.com",
    url="https://github.com/yourusername/fendl_vis",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
) 