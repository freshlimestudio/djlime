#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


setup(
    name='djlime',
    version='0.0.36',
    description='Django goodies.',
    author='Andrey Voronov',
    author_email='voronov84@gmail.com',
    url='http://github.com/freshlimestudio/djlime/',
    long_description=open('README.rst').read(),
    package_dir={'': 'src'},
    packages=find_packages('src'),
    zip_safe=False,
    include_package_data=True,
    license='BSD',
    install_requires=[
        'django>=1.5',
        'simplejson',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
