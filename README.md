# Python Automation Framework #

Python Automation Framework is useful for functional test automation of Mobile Native, Hybrid, Mobile Web & web based application. This framework provides test cases to automate in Behavior Driven approach. It helps to significantly reduce costs involved in setting up Test Automation at any organization. It is a right tool for Web Platform, Mobile Platform (Native, Mobile Web, HTML5, etc) test automation solution using Selenium/Appium.
The framework is built upon Python 3.x and integrates Behave, Webdriver and Appium.

## Installation

    pip3 install git+https://{username}@bitbucket.org/is_corp/qaf-python-automation.git
    pip3 install git+ssh://git@bitbucket.org:is_corp/qaf-python-automation.git

Install forcefully over the existing version

    python3 setup.py install --force
    pip3 install . --upgrade

## Challenges
* Complex syntaxes to write and modify in reference with other programming languages means to be “one line of code at a time"
* Complex design patterning not followed properly let say including Singleton classes and Page factory concepts
* No support of wide range of soft assertions and predefined helper functions
* Redundant efforts in creating Selenium/Appium environment level common tasks and utilities
* Rigid support of not having single point of control to manage iOS, Android and Web all locators
* No Support of reporting provided in Behave BDD framework

## Dependencies

| Dependencies | Description |
| --- | --- |
| selenium | Web Automation Framework |
| webdriver-manager | Automated Driver Manager |
| appium | Mobile Automation Framework |
| behave | Behavior-driven development |
| PyTest | Test Framework |
| PyHamcrest | Matcher Library |
| jmespath | Json Query Language |
| webdriver-manager | Automated Driver Manager |

## Technical Insight
For Python automation, following are the tools details:

* Learn Basic Python
* behave: behave is behaviour-driven development, Python style.
* Logger: Python automation framework is supporting Logger to log details. People can also customize logger as per the requirements.
* Resources: Python automation framework will load all the locators, messages, application properties & other parameters which are defined in .plist or .ini files inside resources directory.
* Web Element: Python automation framework provides custom element to access custom methods like click, send keys, wait for present, verify present, assert present, etc.

## Application Properties
Key  | Usage
------------- | -------------
selenium.wait.timeout | Default wait time to be used by framework by wait/assert/verify methods
remote.server | Remote server url, which will be considered if configured remote driver. e.g. http://localhost:, localhost, 127.0.0.1, etc..
remote.port | Remote server port, which will be considered if configured remote driver
driver.name | Driver to be used, for instance firefoxDriver or firefoxRemoteDriver etc..
driver.capabilities | Specify additional capability by name with this prefix that can applicable for any driver. 
driver.additional.capabilities | Specify multiple additional capabilities as map that can applicable for any driver
{0}.additional.capabilities | Specify multiple additional capabilities as map that can applicable for specific driver. For example, chrome.additional.capabilities.
{0}.capabilities | Specify additional capability by name with this prefix that can applicable for specific driver. For example, chrome.capabilities.
env.baseurl | Base URL of AUT to be used.
env.resources | File or directory to load driver specific resources, for instance driver specific locators.
wd.command.listeners | List of web driver command listeners (fully qualified class name that abstract qaf.automation.ui.webdriver.abstract_listener.DriverListener) to be registered.
we.command.listeners | List of web element command listeners (fully qualified class name that abstract qaf.automation.ui.webdriver.abstract_listener.ElementListener) to be registered.
ws.command.listeners | List of web service command listeners (fully qualified class name that abstract qaf.automation.ws.rest.ws_listener.WsListener) to be registered.
env.default.locale | Local name from loaded locals that need to treated as default local
executable.path | Directory path where you can put executable file. For example, chromedriver, safaridriver, etc..
testing.approach | e.g. behave, pytest