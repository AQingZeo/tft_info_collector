from setuptools import setup, find_packages

setup(
    name="tft-collector",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "typer",
        "rich",
        "pydantic",
        "python-dotenv",
        "httpx",
        "ujson"
    ],
    entry_points={
        "console_scripts": [
            "tft-collector=tft_collector.cli:app"
        ]
    }
)