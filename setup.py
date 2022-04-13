from setuptools import setup, find_packages

try:
    with open('README.md') as f:
        readme = f.read()
except FileNotFoundError:
    readme = ""

setup(name='qaf-python-automation',
      version='1.0.0',
      description='This is Automation framework for Python developed by Infostretch',
      author='Nishith Shah',
      author_email='nishith.shah@infostretch.com',
      license='[]',

      # The project's main homepage.
      url='',

      long_description=readme,
      long_description_content_type="text/markdown",
      maintainer_email='nishith.shah@infostretch.com',

      # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[

          # How mature is this project? Common values are
          #   3 - Alpha
          #   4 - Beta
          #   5 - Production/Stable
          'Development Status :: 4 - Beta',

          # Indicate who your project is intended for
          'Intended Audience :: QE Automation',

          'Natural Language :: English',
          'Operating System :: OS Independent',

          'License :: OSI Approved :: MIT License',
          # Specify the Python versions you support here. In particular, ensure
          'Programming Language :: Python :: 3'
          'Topic :: Software Development :: Quality Assurance',
          'Topic :: Software Development :: Testing',
      ],

      keywords='automation, python-selenium, python-automation, appium, python-appium',
      packages=find_packages(),
      python_requires=">=3.6",
      package_data={
          'qaf.automation': ['config/*.ini']
      },
      install_requires=[
          'selenium==3.14.1',
          'Appium-Python-Client==0.48',
          'behave==1.2.6',
          'PyHamcrest==1.9.0',
          'requests==2.18.4',
          'jmespath==1.0.0',
          'webdriver-manager==3.5.4'
      ],
      zip_safe=False)
