# alkh [al-khwarizmi]
### Algorithmic python debugging
### Convert your debugger stack to jupyter notebook

## Installation
pip install alkh

## Usage

import alkh

alkh.take_it_offline('path-of-notebooks-directory')

or

bash:

export ALKH_NOTEBOOKS_PATH='path-to-notebooks-directory'

python:

import alkh

alkh.take_it_offline()

## Usage flow example
Stop at breakpoint within PyCharm  
![](https://github.com/erez-aharonov/alkh/blob/main/readme_files/take-it-offline-0.png?raw=true)  
Use Console to run code within debugger  
![](https://github.com/erez-aharonov/alkh/blob/main/readme_files/take-it-offline-1.png?raw=true)  
Run: import alkh  
![](https://github.com/erez-aharonov/alkh/blob/main/readme_files/take-it-offline-2.png?raw=true)  
Run: alkh.take_it_offline('path-of-notebooks-directory')  
![](https://github.com/erez-aharonov/alkh/blob/main/readme_files/take-it-offline-3.png?raw=true)  
Start Jupyter  
![](https://github.com/erez-aharonov/alkh/blob/main/readme_files/take-it-offline-4.png?raw=true)  
Run the notebook  
![](https://github.com/erez-aharonov/alkh/blob/main/readme_files/take-it-offline-5.png?raw=true)  