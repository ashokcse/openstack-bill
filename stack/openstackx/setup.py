import os
import shutil
import sys
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

dst = 'debian/openstackx/var/lib/nova/'
os.system('rm -rf %s' % dst)
shutil.copytree('extensions', '%s/extensions' % dst)

requirements = ['httplib2']
if sys.version_info < (2,6):
    requirements.append('simplejson')

setup(
    name = "openstackx",
    version = "0.2",
    description = "Client library extensions for the OpenStack API",
    long_description = read('README.rst'),
    url = 'http://github.com/cloudbuilders/openstackx/',
    license = 'Apache 2.0',
    author = 'Anthony Young',
    author_email = 'sleepsonthefloor@gmail.com',
    packages = find_packages(exclude=['tests']),
    classifiers = [
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: Apache 2.0 License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    namespace_packages = ["openstackx"],
    install_requires = requirements,
    tests_require = ["nose", "mock"],
    test_suite = "nose.collector",
)

