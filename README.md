## pySTOPS
A simple utility for parsing and reading FTA STOPS outputs with python and Pandas. The tool currently supports parsing tables 2.04, 2.05, 2.07, 2.08, 3.01, and 9.01. More table parsers coming soon.

Happily accepting additions.

## Installation
The project relies on Python.

3. Create a pySTOPS-oriented virtual python environment. Recommend using a Anaconda Conda virtual env with the environment.yml included in this repository.
```
>>conda env create -f environment.yml
```
4. Switch the Virtual Env
```
conda activate pystops
```
5. Use the setup.py to install the package.
```
>>python setup.py install
```
6. Move to the test folder.
```
>>cd tests
```

7. Run example
```python
python example.py
```
