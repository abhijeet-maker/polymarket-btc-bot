from setuptools import setup, find_packages

setup(
    name="polymarket-btc-bot",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "py-clob-client>=0.1.2",
        "websocket-client>=1.6.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.950",
        ],
    },
    entry_points={
        "console_scripts": [
            "polymarket-bot=src.bot:main",
        ],
    },
)