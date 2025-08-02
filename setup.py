from setuptools import setup, find_packages

setup(
    name="ServicesSoundAlexa",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},  # Importante: apunta al código en 'src/'
    include_package_data=True,
    author="Carlos Henao",
    author_email="tucorreo@example.com",
    description="Sistema para usar Alexa como altavoz del PC",
    keywords="alexa, audio, streaming",
    python_requires=">=3.11",
)
