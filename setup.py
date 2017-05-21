from setuptools import setup, find_packages


kw = dict(
    name='xsegment',
    version='0.2.0',
    description='chinese words segment use regular ',
    author='intoblack',
    author_email='intoblack86@gmail.com',
    url='https://github.com/intoblack/xsegment',
    download_url='https://github.com/intoblack/xsegment',
    platforms='all platform',
    packages = find_packages(),
    package_data = {
        '': ['*.*'],
        'dict': ['*.*'],
    }
)

setup(**kw)
