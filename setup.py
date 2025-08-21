"""
This setup.py is an essential  part of packaging and distributing Python projects.
It defines the package metadata, dependencies, and entry points for the project.
This file is crucial for ensuring that the project can be easily installed and used by others.
"""
from setuptools import setup, find_packages
from typing import List

def get_requirements(file_path: str) -> List[str]:
    """
    This function will return a list of requirements
    """
    requirement_list:List[str] = []
    try :
        with open(file_path, 'r') as file:
            lines= file.readlines()
        for line in lines:
            requirement=line.strip()
            if requirement and  requirement != '-e .':
                requirement_list.append(requirement)
    except FileNotFoundError:
        print("requirements.txt file not found. Please ensure it exists in the project directory.")
    return requirement_list

setup(
    name='networksecurity',
    version='0.0.1',
    author='Rahul Manchanda',       
    author_email="rahulmanchanda015@gmail.com",
    packages=find_packages(),
    install_requires=get_requirements('requirements.txt'),
)                          