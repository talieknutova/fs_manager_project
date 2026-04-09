from setuptools import setup, find_packages

setup(
    name='fs_manager',
    version='1.0.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'fs-manager=fs_manager.cli:main',
            'fs-manager-gui=fs_manager.gui:start',  # Новая точка входа для графического интерфейса
        ],
    },
    author='Your Name',
    description='A simple file system manager CLI and GUI utility.',
)