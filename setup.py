#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Setup file for PyScaffold.

    Important note: Since PyScaffold is self-using and depends on
    setuptools-scm, it is important to run `python setup.py egg_info` after
    a fresh checkout. This will generate some critically needed data.
"""

import inspect
import os
import sys
from distutils.cmd import Command
try:  # Python 3
    from configparser import ConfigParser
except ImportError:  # Python 2
    from ConfigParser import SafeConfigParser as ConfigParser

from setuptools import setup, find_packages

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"
__location__ = os.path.join(os.getcwd(), os.path.dirname(
    inspect.getfile(inspect.currentframe())))


def build_cmd_docs():
    try:
        from sphinx.setup_command import BuildDoc
    except ImportError:
        class NoSphinx(Command):
            user_options = []

            def initialize_options(self):
                raise RuntimeError("Sphinx documentation is not installed, "
                                   "run: pip install sphinx")

        return NoSphinx
    else:
        return BuildDoc


def read(fname):
    with open(os.path.join(__location__, fname)) as fh:
        content = fh.read()
    return content


def version2str(version):
    if version.exact or not version.distance > 0:
        return version.format_with('{tag}')
    else:
        distance = version.distance
        version = str(version.tag)
        if '.dev' in version:
            version, tail = version.rsplit('.dev', 1)
            assert tail == '0', 'own dev numbers are unsupported'
        return '{}.post0.dev{}'.format(version, distance)


def local_version2str(version):
    if version.exact:
        if version.dirty:
            return version.format_with('+dirty')
        else:
            return ''
    else:
        if version.dirty:
            return version.format_with('+{node}.dirty')
        else:
            return version.format_with('+{node}')


def get_install_requirements(path):
    with open(os.path.join(__location__, path)) as fh:
        content = fh.read()
    return [req for req in content.splitlines() if req != '']


def read_setup_cfg():
    cfg = ConfigParser()
    cfg.read(os.path.join(__location__, 'setup.cfg'))
    return {k: v for k, v in cfg.items('metadata')}


def setup_package():
    docs_path = os.path.join(__location__, 'docs')
    docs_build_path = os.path.join(docs_path, '_build')
    needs_pytest = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
    pytest_runner = ['pytest-runner'] if needs_pytest else []
    requirements = get_install_requirements('requirements.txt')
    command_options = {
        'docs': {'build_dir': ('setup.py', docs_build_path),
                 'config_dir': ('setup.py', docs_path),
                 'source_dir': ('setup.py', docs_path)},
        'doctest': {'build_dir': ('setup.py', docs_build_path),
                    'config_dir': ('setup.py', docs_path),
                    'source_dir': ('setup.py', docs_path),
                    'builder': ('setup.py', 'doctest')},
        'pytest': {'addopts': ('setup.py', 'tests '
                                            '--cov pyscaffold '
                                            '--cov-report term-missing '
                                            '--verbose')}
    }
    entry_points = {
        'console_scripts': ['putup=pyscaffold.cli:run'],
        'distutils.setup_keywords':
            ['use_pyscaffold=pyscaffold.integration:pyscaffold_keyword']
    }
    setup_cfg = read_setup_cfg()
    setup(name=setup_cfg['name'],
          url=setup_cfg['home-page'],
          author=setup_cfg['author'],
          author_email=setup_cfg['author-email'],
          description=setup_cfg['summary'],
          long_description=read(setup_cfg['description-file']),
          license=setup_cfg['license'],
          classifiers=[c.strip() for c in setup_cfg['classifiers'].split(',')],
          setup_requires=['setuptools_scm'] + pytest_runner,
          tests_require=['pytest-cov', 'pytest'],
          install_requires=requirements,
          extras_require={'ALL': ["django", "cookiecutter"]},
          package_data={'pyscaffold': ['templates/*']},
          cmdclass={'docs': build_cmd_docs(), 'doctest': build_cmd_docs()},
          command_options=command_options,
          entry_points=entry_points,
          packages=find_packages(exclude=['tests', 'tests.*']),
          use_scm_version={'version_scheme': version2str,
                           'local_scheme': local_version2str})


if __name__ == '__main__':
    setup_package()
