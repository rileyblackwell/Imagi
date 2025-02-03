from setuptools import setup, find_packages

setup(
    name="olive_20250203191758",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'django',
        'djangorestframework',
        'djangorestframework-simplejwt',
        'django-cors-headers',
    ],
)
