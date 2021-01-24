import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cronenbroguelike",
    version="0.0.4",
    author="The Arch Cronenbrogues",
    author_email="cronenbrogues@googlegroups.com",
    description="A text-based-body-horror-rogue-like game.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Cronenbrogues/cronenbroguelike",
    packages=setuptools.find_packages(),
    python_requires=">=3.8",
)
