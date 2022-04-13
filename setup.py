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
      maintainer_email='nishith.shah@infostretch.com',

      # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[

          # How mature is this project? Common values are
          #   3 - Alpha
          #   4 - Beta
          #   5 - Production/Stable
          'Development Status :: 4 - Beta',

          # Indicate who your project is intended for
          'Intended Audience :: QE Automatin',

          'Natural Language :: English',
          'Operating System :: OS Independent',

          # Specify the Python versions you support here. In particular, ensure
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7'
      ],

      keywords='automation, python-selenium, python-automation, appium, python-appium',
      packages=find_packages(),
      package_data={
          'infostretch.automation': ['config/*.ini']
      },
      install_requires=[
          'Appium-Python-Client==0.48',
          'behave==1.2.6',
          'selenium==3.14.1',
          'PyHamcrest==1.9.0',
          'requests==2.18.4',
          'jmespath==1.0.0',
          'webdriver-manager==3.5.4'
      ],
      zip_safe=False)
