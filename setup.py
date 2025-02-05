from setuptools import setup

setup(
    name="nordigen_account",
    version="0.3.1",
    author="Rahul Parmar",
    author_email="rahulparmaruk@gmail.com",
    description="A Python package to interact with Nordigen API for bank account management.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/rahulpdev/nordigen_account",
    include_package_data=True,
    packages=["nordigen_account"],
    install_requires=[
        "nordigen>=1.4.1",
    ],
    python_requires=">=3.7",
    license="MIT",
    keywords="nordigen api bank accounts finance",
)
