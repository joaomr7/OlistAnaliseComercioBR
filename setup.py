import setuptools

PROJECT_NAME = 'review_analysis'
PROJECT_VERSION = '0.0.1'
PROJECT_AUTHOR = 'João Marcos Ressetti'
PROJECT_DESCRIPTION = 'Review analysis system.'

setuptools.setup(
    name=PROJECT_NAME,
    version=PROJECT_VERSION,
    author=PROJECT_AUTHOR,
    description=PROJECT_DESCRIPTION,
    packages=setuptools.find_packages()
)