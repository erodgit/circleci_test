from setuptools import setup

setup(
    name='Python Testing for rippled',
    version='0.1dev',
    author='Kimon Papahadjopoulos',
    author_email='kimonp@interledgerfx.com',
    packages=['bank_bot'],
    setup_requires=['pytest-runner', 'requests', 'dateutils'],
    tests_require=['pytest', 'robotframework'],
    license='PolySign Commercial',
    long_description=open('README.md').read(),
)
