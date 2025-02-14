from setuptools import setup, find_packages

CLASSIFIERS = [
    "Intended Audience :: Developers",
    "Topic :: Internet",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
setup(
    name="gmail2notification",
    version="0.1.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "g2notification = gmail2notification.scripts.g2notification:command",
        ],
    },
    classifiers=CLASSIFIERS,
    keywords="gmail line notifier notification",
    install_requires=[
        "google-api-core==2.23.0",
        "google-api-python-client==2.153",
        "google-auth==2.36.0",
        "google-auth-httplib2==0.2.0",
        "google-auth-oauthlib==0.4.2",
        "googleapis-common-protos==1.66.0",
        "line-notify==0.1.4",
        "toml==0.10.2",
        "tomli==2.0.1",
        "python-dotenv==0.21.1",
    ],
    extras_require={
        # List development-specific dependencies herepy
        "dev": [
            "pytest==7.4.0",
        ],
    },
)
