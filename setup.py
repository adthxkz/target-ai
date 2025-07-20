from setuptools import setup, find_packages

setup(
    name="target-ai",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn>=0.24.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.5.2",
        "openai>=1.0.0",
        "python-telegram-bot>=20.0",
        "httpx>=0.25.2",
        "python-multipart>=0.0.6",
        "facebook-business>=18.0.0",
        "SQLAlchemy>=1.4.41,<2.0.0",
        "aiosqlite>=0.19.0",
    ],
    python_requires=">=3.8",
)
