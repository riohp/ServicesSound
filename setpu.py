from setuptools import setup, find_packages

setup(
    name="ServicesSoudAlexa",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pyaudio>=0.2.11",
        "flask>=1.1.2",
        "numpy>=1.16.6",
        "zeroconf>=0.38.4",
        "netifaces>=0.11.0",
    ],
    author="Carlos Henao",
    author_email="@email.com",
    description="Sistema para usar Alexa como altavoz del PC",
    keywords="alexa, audio, streaming",
    python_requires=">=3.12",
)