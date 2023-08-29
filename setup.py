import setuptools

with open('./README.md', 'r', encoding = 'utf-8') as f:
    longDescription = f.read()

setuptools.setup(
    name = 'CheeseAPI',
    version = '0.1.4',
    author = 'Cheese Unknown',
    author_email = 'cheese@cheese.ren',
    description = '一款web协程框架',
    long_description = longDescription,
    long_description_content_type = 'text/markdown',
    url = 'https://github.com/CheeseUnknown/CheeseAPI',
    license = 'MIT',
    classifiers = [
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.11'
    ],
    keywords = 'api framework backend asyncio',
    python_requires = '>=3.11',
    install_requires = [
        'CheeseType',
        'CheeseLog',
        'xmltodict',
        'blinker',
        'websockets',
        'uvloop',
        'httptools'
    ],
    packages = setuptools.find_packages()
)
