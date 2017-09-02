from setuptools import setup

setup(
    entry_points={
        'console_scripts': ['pyler=pyler.__main__:main'],
    },
)
