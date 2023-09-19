#  Copyright (c) 2022 Infostretch Corporation
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#  #
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

from setuptools import setup, find_packages

try:
    with open('README.md') as f:
        readme = f.read()
except FileNotFoundError:
    readme = ""

setup(name='qaf-python',
      version='1.0.0',
      description='This is Automation framework for Python developed by Infostretch',
      authors='Nishith Shah, Chirag Jayswal',
      author_email='nshthshah[at]gmail.com, cjayswal[at]gmail.com',
      license='MIT',

      # The project's main homepage.
      url='https://github.com/qmetry/qaf-python',

      long_description=readme,
      long_description_content_type="text/markdown",
      maintainer_email='cjayswal[at]gmail.com',
      entry_points={"pytest11": ["qaf = qaf.pytest.qaf_pytest_plugin"]},
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Topic :: Software Development :: Quality Assurance',
          'Topic :: Software Development :: Testing',
      ],

      keywords='qaf, bdd, automation, python-selenium, python-automation, appium, python-appium',
      packages=find_packages(),
      python_requires=">=3.6",
      package_data={
          'qaf.automation': ['config/*.ini']
      },
      install_requires=[
          'selenium>=4.9.1',
          'Appium-Python-Client>=2.10.1',
          'behave>=1.2.6',
          'PyHamcrest>=1.9.0',
          'requests>=2.31.0',
          'jmespath>=1.0',
          'webdriver-manager',
          'simpleeval>=0.9.13',
          'pytest~=7.3.1'
      ],
      zip_safe=False)
