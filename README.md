# QAF-Python Automation Framework #

The QAF-Python Automation Framework is designed to facilitate functional test automation for various platforms,
including Web, Mobile Web, Mobile Hybrid apps, Mobile Native apps, and web services. It offers a comprehensive set of
features for driver and resource management, data-driven testing, and BDD support using QAF BDD2. The framework is built
on Python 3.x and seamlessly integrates with popular tools like pytest, WebDriver, and Appium.

## Installation

    pip install git+https://github.com/qmetry/qaf-python.git@master

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
    sendKeys("username.txt.ele", username)
    sendKeys("password.txt.ele", password)
    click("login.btn.ele")
```

You have the flexibility to write your tests using **either** Python as pytest **or** in a behavior-driven development (
BDD)
style. This allows you to choose the approach that best suits your preferences and project requirements.

### Testcase authoring in BDD

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
pytest
features  # all files from features directory 
pytest
features / login.feature  # single file
pytest
features - -dryrun  # dry-run mode
```

you can use pytest mark or qaf metadata filter.

```python
pytest
features - m
web - -metadata - filter
"module == 'login' and storyKey in ['PRJ001', 'PRJ005']"
```

### Test case authoring in python script (pytest)

```python
from qaf.automation.step_def.common_steps import verify_present, verify_text
from proj.steps.commonsteps import *


@pytest.mark.web
@pytest.mark.mobile
@metadata(storyKey="TC001", module="login")
class loginFunctionality:
    @metadata("smoke", testCaseId="TC001")
    def test_login():
        open_app()
        login(getBundle().get_string('valid.user.name'), getBundle().get_string('valid.user.password'))
        verify_present(None, 'logout.btn.ele')

    @dataprovider(datafile="resources/${env.name}/logindata.csv")
    def test_login(testdata):
        open_app()
        login(testdata.get('user-name'), testdata.get('password'))
        verify_text(None, 'error.text.ele', testdata.get('error-msg'))
```

#### run test

same as running normal pytest with additional meta-data filter as shown in example above

## Features

Here is list of features in addition to features supported by pytest

- **Web, Mobile, and Web Services Testing**: The framework supports test automation for Web applications, Mobile Web,
  Mobile Hybrid apps, Mobile Native apps, and web services. It provides a unified solution for testing different
  platforms.

- **Configuration Management**: The framework offers robust configuration management capabilities. It supports various
  configuration file formats such as ini, properties, wsc, loc, locj, and wscj. This allows you to manage and organize
  your test configuration efficiently.

- **Driver Management**: The framework simplifies the management of WebDriver and Appium drivers. It supports on-demand
  driver session creation and automatic teardown, making it easy to without worring of set up and clean up driver
  sessions. You can configure the driver properties through properties files, enabling flexibility in driver
  configuration.

- **Driver and Element Command Listeners**: The framework allows you to register driver command listeners and element
  command listeners. This feature enables you to intercept and modify driver and element commands, facilitating custom
  behavior and extensions.

- **Support for Multiple Driver Sessions**: QAF-Python supports multiple driver sessions in the same test. This means
  you can test scenarios that involve multiple browser instances or multiple mobile devices simultaneously.

- **Wait/Assert/Verify Functionality**: The framework provides convenient methods for waiting, asserting, and verifying
  element states. It includes automatic waiting capabilities, ensuring synchronization between test steps and
  application behavior.

- **Locator Repository**: QAF-Python includes a locator repository for managing web and mobile element locators. The
  repository allows you to store and organize element locators, making them easily accessible and reusable across tests.

- **Request Call Repository**: For testing web services, the framework provides a repository for managing web service
  request calls. You can store and manage your API requests, making it convenient to handle different API scenarios and
  payloads.

- **Data-Driven Testing**: QAF-Python supports data-driven testing by integrating with CSV and JSON data files. You can
  parameterize your tests and iterate over test data, enabling you to run tests with different input values and expected
  results.

- **Native Pytest Implementation of QAF-BDD2**: The framework offers a native implementation of QAF-BDD2 in pytest. This
  allows you to write BDD-style tests using the Given-When-Then syntax and organize them into feature files. You can use
  metadata annotations and tags to categorize and filter tests based on criteria such as story key, module, and more.

- **Step Listener with Retry Step Capability**: QAF-Python includes a step listener that provides retry capabilities for
  test steps. If a step fails, the framework can automatically retry the step for a specified number of times, enhancing
  the robustness of your tests.

- **Dry Run Support**: You can perform a dry run of your tests using the framework. This allows you to check the test
  execution flow, identify any errors or issues, and ensure that the tests are set up correctly before running them for
  real.

- **Metadata Support with Metadata Filter**: QAF-Python supports metadata annotations and filters. You can assign
  metadata to tests, such as story key, module, or custom tags, and use metadata filters to selectively run tests based
  on specific criteria.

- **Detailed Reporting**: The framework provides detailed reporting capabilities, giving you insights into test
  execution results. You can generate comprehensive reports that include test status, step-level details, screenshots,
  and other relevant information.

- **Repository Editor**: QAF offers a repository editor tool that allows you to create and update the locator
  repository and request call repository easily. The editor provides a user-friendly interface for managing and
  organizing your locators and API requests. You can
  use [repository editor](https://qmetry.github.io/qaf/latest/repo_editor.html) to create/update locator
  repository and request call repository.

**Driver Management benefits**

The framework simplifies the management of WebDriver and Appium drivers. It supports on-demand driver session creation
and automatic teardown, making it easy to set up and clean up driver sessions. This feature allows you to focus on
writing test scripts rather than dealing with driver setup and cleanup processes.

- **On-Demand Driver Session Creation**: With the framework's on-demand driver session creation, framework dynamically
  creates driver instances whenever you need them during test execution. This ensures that the drivers are available
  precisely when required, reducing resource wastage and enhancing test execution efficiency.

- **Automatic Teardown**: After test execution or when a test session ends, the framework automatically tears down the
  driver sessions. This cleanup process prevents any potential resource leaks and optimizes the utilization of testing
  resources.

- **Driver Configuration via Properties Files**: The framework allows you to configure driver through properties files.
  This approach provides a convenient and organized way to manage various driver settings, such as browser preferences,
  timeouts, and capabilities, in separate configuration files. It makes the driver configuration process more manageable
  and less error-prone.

- **Flexibility in Driver Configuration**: By using properties files for driver configuration, you gain flexibility in
  customizing the driver behavior. You can easily update the properties files to modify driver settings without
  modifying the test scripts, which enhances maintainability and reusability of your automation code.

The Driver Management feature in the framework streamlines the process of working with WebDriver and Appium drivers. It
ensures that driver sessions are readily available when needed and automatically handles cleanup after test execution.
Additionally, the flexibility in driver configuration through properties files simplifies the management of driver
settings, improving the overall efficiency and organization of your test automation process.

## Properties used by framework

 Key                            | Usage                                                                                                                                                            
--------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------
 selenium.wait.timeout          | Default wait time to be used by framework by wait/assert/verify methods                                                                                          
 remote.server                  | Remote server url, which will be considered if configured remote driver. e.g. http://localhost:, localhost, 127.0.0.1, etc..                                     
 remote.port                    | Remote server port, which will be considered if configured remote driver                                                                                         
 driver.name                    | Driver to be used, for instance firefoxDriver or firefoxRemoteDriver etc..                                                                                       
 driver.capabilities            | Specify additional capability by name with this prefix that can applicable for any driver.                                                                       
 driver.additional.capabilities | Specify multiple additional capabilities as map that can applicable for any driver                                                                               
 {0}.additional.capabilities    | Specify multiple additional capabilities as map that can applicable for specific driver. For example, chrome.additional.capabilities.                            
 {0}.capabilities               | Specify additional capability by name with this prefix that can applicable for specific driver. For example, chrome.capabilities.                                
 env.baseurl                    | Base URL of AUT to be used.                                                                                                                                      
 env.resources                  | File or directory to load driver specific resources, for instance driver specific locators.                                                                      
 wd.command.listeners           | List of web driver command listeners (fully qualified class name that abstract qaf.automation.ui.webdriver.abstract_listener.DriverListener) to be registered.   
 we.command.listeners           | List of web element command listeners (fully qualified class name that abstract qaf.automation.ui.webdriver.abstract_listener.ElementListener) to be registered. 
 ws.command.listeners           | List of web service command listeners (fully qualified class name that abstract qaf.automation.ws.rest.ws_listener.WsListener) to be registered.                 
 env.default.locale             | Local name from loaded locals that need to treated as default local                                                                                              
 testing.approach               | e.g. behave, pytest                                                                                                                                              

### License

This project is licensed under the MIT License.

### Acknowledgements

We would like to thank the pytest community for their excellent work in developing a robust and extensible testing
framework. Their contributions have been invaluable in building this enhanced test automation framework.