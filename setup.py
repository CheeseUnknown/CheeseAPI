import setuptools

with open('./README.md', 'r', encoding = 'utf-8') as f:
    longDescription = f.read()

setuptools.setup(
    name = 'CheeseAPI',
    version = '0.0.5',
    author = 'Cheese Unknown',
    author_email = 'cheese@cheese.ren',
    description = '一款基于uvicorn的web协程框架',
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
    entry_points = {
        'console_scripts': [
            'CheeseAPI = CheeseAPI.command:command'
        ]
    },
    install_requires = [
        'uvicorn[standard]',
        'CheeseType',
        'CheeseLog',
        'xmltodict',
        'blinker'
    ],
    packages = setuptools.find_packages()
)
