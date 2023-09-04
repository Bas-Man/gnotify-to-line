from setuptools import setup, find_packages

setup(
    name='gmail2line',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'google-api-core==1.25.0',
        'google-api-python-client==1.12.8',
        'google-auth==1.24.0',
        'google-auth-httplib2==0.0.4',
        'google-auth-oauthlib==0.4.2',
        'googleapis-common-protos==1.52.0',
        'line-notify==0.1.4',
        'toml==0.10.2',
        'tomli==2.0.1',
    ],
    extras_require={
        "dev": [
            "pytest==7.4.0",
            'python-dotenv==0.21.1',
            # List development-specific dependencies here
        ],
    },
    entry_points={
        'console_scripts': [
            'g2line = gmail2line.main:cli',
        ],
    },
)
