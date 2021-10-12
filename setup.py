'''
Created on 12 juin 2020

@author: tleduc

https://packaging.python.org/tutorials/packaging-projects/
'''
from setuptools import setup, find_packages

with open('README.md') as readme_file:
    README = readme_file.read()

# with open('HISTORY.md') as history_file:
#     HISTORY = history_file.read()

# EXCLUSION_LIST = ['tests', 'tests.*']
EXCLUSION_LIST = ['tests', 'tests.*', 't4gpd.future', 't4gpd.future.*']

setup_args = dict(
    name='t4gpd',
    # version='0.0.1',
    version=open('t4gpd/_version.py').readlines()[-1].split()[-1].strip("\"'"),
    description='Set of tools based on Python, GeoPandas and Shapely to achieve urban geoprocessing',
    long_description_content_type='text/markdown',
    long_description=README + '\n\n',
    # long_description=README + '\n\n' + HISTORY,
    license='GPLv3+',
    packages=find_packages(exclude=EXCLUSION_LIST),
    author='Thomas Leduc',
    author_email='thomas.leduc@crenau.archi.fr',
    keywords=['Geospatial analysis', 'Urban form', 'Urban morphology', 'Isovist'],
    url='https://t4gpd-docs.readthedocs.io',
    download_url='https://sourcesup.renater.fr/frs/?group_id=463',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Education',
        'Topic :: Scientific/Engineering :: GIS',
    ],
    python_requires='>=3.6',
)

install_requires = [
    # 'matplotlib>=2.0.1',
    # 'numpy',
    # 'geopandas',
    # 'shapely'
]

if __name__ == '__main__':
    setup(**setup_args, install_requires=install_requires)
