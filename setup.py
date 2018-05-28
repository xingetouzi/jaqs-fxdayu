import codecs

try:
    from pip._internal.req import parse_requirements # for pip >= 10
except ImportError:
    from pip.req import parse_requirements

from os.path import dirname, join
from setuptools import (
    find_packages,
    setup,
)


def readme():
    with codecs.open('README.md', 'r', encoding='utf-8') as f:
        return f.read()


def version():
    with open(join(dirname(__file__), 'jaqs_fxdayu', 'VERSION.txt'), 'rb') as f:
        return f.read().decode('ascii').strip()


requirements = [str(ir.req) for ir in parse_requirements("requirements.txt", session=False)]
setup(
    name='jaqs_fxdayu',
    version=version(),
    packages=find_packages(exclude=["examples", "tests", "tests.*", "docs"]),
    author='xingetouzi',
    author_email='public@fxdayu.com',
    license='Apache License v2',
    package_data={'': ['*.csv', '*.txt']},
    url='https://github.com/xingetouzi/jaqs_fxdayu',
    keywords="quantiatitive trading research finance",
    install_requires=requirements,
    description='Open source quantitative research&trading framework, base on https://github.com/quantOS-org/JAQS',
    long_description=readme(),
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python',
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: Chinese (Simplified)",
        "Natural Language :: English",
        'Operating System :: Microsoft :: Windows',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
