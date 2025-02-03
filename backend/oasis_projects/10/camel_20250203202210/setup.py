from setuptools import setup, find_packages

setup(
    name="camel_20250203202210",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'django',
        'djangorestframework',
        'djangorestframework-simplejwt',
        'django-cors-headers',
    ],
)
