from setuptools import setup, find_packages

setup(
    name="agent-bridge",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "httpx>=0.28.0",
        "pydantic>=2.10.0",
    ],
    python_requires=">=3.11",
)
