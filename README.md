# Python Automation Framework #

Python Automation Framework can be useful for functional test automation of Web, Mobile Web, Mobile Hybrid app, Mobile Native app, & web-services. 
This framework provides driver and resource management, data driven capability along with QAF BDD2 support. 
It helps to significantly reduce costs involved in setting up Test Automation at any organization. 
It is a right tool for Web Platform, Mobile Platform (Native, Mobile Web, HTML5, etc) test automation solution using Selenium/Appium.
The framework is built upon Python 3.x and integrates pytest, Webdriver and Appium.

## Installation

    pip install qaf-python

## Run Test
    pytest [<options>]

## Quick Example

Steps file: `proj/steps/commonsteps.py`
```python
from qaf.automation.bdd2 import *
from qaf.automation.step_def.common_steps import *

@step("user is on application home")
def open_app():
    get("/")

@step("login with {username} and {password}")
def login(username, password):
    sendKeys("username.txt.ele",username)
    sendKeys("password.txt.ele",password)
    click("login.btn.ele")
```
You can write tests either in python as pytest or in bdd.
### Option 1 BDD
BDD file: `features/login.feature`
```gherkin
@web @mobile 
@storyKey:PRJ001 @module:login
Feature: Login functionality
  
  @smoke 
  @testCaseId:TC001 
  Scenario: user should be able to login into application
    Given user is on application home
    When login with '${valid.user.name}' and '${valid user.password}'
    Then verify 'logout.btn.ele' is present
    
  @datafile:resources/${env.name}/logindata.csv
  Scenario: user should be able to login into application
    Given user is on application home
    When login with '${user-name}' and '${password}'
    Then verify 'error.text.ele' text is '${error-msg}'
```
#### Run tests
You can run BDD same as running normal pytest
```python
pytest features # all files from features directory 
pytest features/login.feature #single file
pytest features --dryrun # dry-run mode
```
you can use pytest mark or qaf metadata filter.
```python
pytest features -m web --metadata-filter "module == 'login' and storyKey in ['PRJ001', 'PRJ005']"
```


### Option 2 pytest

```python
from qaf.automation.step_def.common_steps import verify_present, verify_text
from proj.steps.commonsteps import *

@pytest.mark.web
@pytest.mark.mobile
@metadata(storyKey="TC001",module="login")
class loginFunctionality:
  @metadata("smoke",testCaseId="TC001")
  def test_login():
    open_app()
    login(getBundle().get_string('valid.user.name'),getBundle().get_string('valid.user.password'))
    verify_present(None, 'logout.btn.ele')

  @dataprovider(datafile="resources/${env.name}/logindata.csv")
  def test_login(testdata):
    open_app()
    login(testdata.get('user-name'),testdata.get('password'))
    verify_text(None, 'error.text.ele', testdata.get('error-msg'))
```
#### run test
same as running normal pytest with additional meta-data filter as shown in example above
    
## Features
Here is list of features in addition to features supported by pytest
* Web, mobile and web-services 
* Configuration management with support of `ini`, `properties`, `wsc`, `loc`, `locj`, `wscj` files
* Driver management
    * ondemand driver session creation and auto teardown
    * driver configuration through properties
    * driver and element command listeners
    * support of multiple driver sessions in same test
    * wait/assert/verify with element, auto wait if required
* Locator repository for web/mobile element locators
* Request call repository for web service requests
* Data-driven test supports CSV, Json
* Native pytest implementation of QAF-BDD2
  * step listener with retry step capability
  * dry run support
* metadata with metadata filter
* QAF detailed reporting

You can use [repository editor](https://qmetry.github.io/qaf/latest/repo_editor.html) to create/update locator repository and request call repository.

## Properties used by framework
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