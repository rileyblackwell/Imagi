from setuptools import setup, find_packages

setup(
    name="novi_amor_20250203185829",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'django',
        'djangorestframework',
        'djangorestframework-simplejwt',
        'django-cors-headers',
    ],
)
