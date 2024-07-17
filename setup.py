from setuptools import setup, find_packages

setup(
    name='nebula-web',
    version='0.1.0',
    description='A custom web server framework',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Raphael Mühlbacher',
    author_email='raphi.muehlbacher@gmail.com',
    url='https://github.com/RaphiMuehlbacher/Nebula',
    download_url='https://github.com/RaphiMuehlbacher/Nebula/archive/refs/tags/v0.1.tar.gz',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'nebula': ['project_template/*', 'project_template/*/*']
    },
    install_requires=[
        "Jinja2~=3.1.4",
        "setuptools~=69.2.0",
        "watchdog~=4.0.1"
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.12',
    ],
    python_requires='>=3.12',
    entry_points={
        'console_scripts': [
            'nebula-admin=nebula.manage:main'
        ]
    },
)
