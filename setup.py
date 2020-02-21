import sys
import versioneer
import setuptools

if sys.version_info < (3,6):
    print("Soundlab requires Python 3.6 or higher please upgrade")
    sys.exit(1)

long_description = \
"""
Soundlab is a python package to analyze and visualize sound data.  Created 
with scientific use in mind. It is in its early stages of development (alpha) 
stage.

"""

setuptools.setup(
    name='soundlab',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=['soundlab', 'soundlab.tests'],
    url='https://github.com/gbeckers/soundlab',
    license='BSD-3',
    author='Gabriel J.L. Beckers',
    author_email='gabriel@gbeckers.nl',
    description='Package to analyse of sound data',
    long_description=long_description,
    long_description_content_type="text/x-rst",
    python_requires='>=3.6',
    install_requires=['sounddata', 'matplotlib', 'pandas'],
    data_files = [("", ["LICENSE"])],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Education',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
    ],
    project_urls={  # Optional
        'Source': 'https://github.com/gbeckers/soundlab',
    }
)

