from setuptools import find_packages, setup


setup(
    name="mcli",
    packages=find_packages(),
    version="0.0.0.1",
    description="mCLI is a CLI application used to analyze malware using Malcore directly from your terminal",
    author="Thomas Perkins",
    author_email="contact@malcore.io",
    install_requires=["requests", "msdk", "tabulate"],
    long_description=open("README.md").read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Internet-2-0/mCLI',
    entry_points={
        'console_scripts': [
            'mcli=mcli.cli_tool:run'
        ]
    }
)
