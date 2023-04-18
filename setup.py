from setuptools import setup, find_packages

setup(
    name='gmail2line',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'google-api-python-client',
        'google-auth-httplib2',
        'google-auth-oauthlib',
        'line-notify==0.1.4',
        'python-dotenv==0.21.1',
        'toml==0.10.2',
        'tomli==2.0.1',
    ],
    entry_points={
        'console_scripts': [
            'g2line = gmail2line.main:cli',
        ],
    },
)
