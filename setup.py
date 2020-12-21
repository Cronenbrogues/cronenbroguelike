import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cronenbroguelike",
    version="0.0.1",
    author="Cory Massaro",
    author_email="cory.massaro@gmail.com",
    description="A body horror, rogue-like, text-based game.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/flosincapite/cronenbroguelike",
    packages=setuptools.find_packages(),
    python_requires='>=3.8',
)
