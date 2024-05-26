# Installation #
## Graphical installer ##
A graphical installer is work in progress and will be released here soon

## Pre built executable ##
### Requirements ### 
 - `gcc` (Will be fixed some time)

 1. Use the [Releases](https://github.com/OffensiverHase/HeiabubuLang/tags) section and download the version for your OS
 2. Put the executable into your [PATH](https://gist.github.com/nex3/c395b2f8fd4b02068be37c961301caa7)
 4. Open a terminal and type `heiabubu  --help` to get started

## Building from source ##
 1. Clone or download the source for this repository
 2. Create a new `Anaconda` or `Miniconda` Environement in the `HeiabubuLang` folder   
    `conda create --name heiabubu python=3.12.1`
 3. Activate the new environment
    `conda activate heiabubu`
 4. Install the dependencies
    `conda install llvmlite`
    `conda install termcolor`
    `pip install pyinstaller`
 5. Build the execuable
    `pyinstaller --onefile -n heiabubu main.py
 6. Add the `dist` folder to your [PATH](https://gist.github.com/nex3/c395b2f8fd4b02068be37c961301caa7)
 7. Open a terminal and type `heiabubu --help` to get started
 
