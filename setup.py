import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt") as fh:
    requirements = fh.read().splitlines()

setuptools.setup(
    name="cronenbroguelike",
    version="2.2.0",
    author="The Arch Cronenbrogues",
    author_email="cronenbrogues@googlegroups.com",
    description="Â̳ tͥ͞e̅̊x̂ͅtͤ͟-b̝͒à͉s͌͜e̮̓d͚̦-b̨͞o̟ͣdͣyͧ͘-h̛͞o̵ͅr̷͍r̺͡ơ̎r̡̞-r͉̉o͇g̦̏u̦̞e͌͘-l͖̃i̇̈́ḱͅe͢͡ gͧ͜a̜̽mͭ͛e̷͍.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    url="https://github.com/Cronenbrogues/cronenbroguelike",
    packages=setuptools.find_packages(exclude=("tests")),
    include_package_data=True,
    python_requires=">=3.8",
)
