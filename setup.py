from setuptools import setup, find_packages

__version__ = "1.2.4"

with open('README.md', 'r') as readme_file:
    long_description = readme_file.read()
    
setup(
    name='rlgym-sim',
    packages=find_packages(),
    version=__version__,
    description='A clone of RLGym for use with RocketSim in reinforcement learning projects.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Lucas Emery, Matthew Allen, Zealan, and Mtheall',
    url='https://github.com/AechPro/rocket-league-gym-sim',
    install_requires=[
        'gym>=0.17',
        'numpy>=1.19',
    ],
    python_requires='>=3.7',
    license='Apache 2.0',
    license_file='LICENSE',
    keywords=['rocket-league', 'gym', 'reinforcement-learning', 'simulation']
)