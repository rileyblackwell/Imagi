from setuptools import setup, find_packages

setup(
    name="dog_20250203203036",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'django',
        'djangorestframework',
        'djangorestframework-simplejwt',
        'django-cors-headers',
    ],
)
