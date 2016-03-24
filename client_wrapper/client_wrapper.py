# Copyright 2016 Measurement Lab
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from datetime import datetime
import pytz
from selenium import webdriver
from selenium.webdriver.support import ui
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException


class TestError(object):
    """Log message of an error encountered in the test.

    Attributes:
        timestamp: Datetime of when the error was observed
        message: String message describing the error.
    """

    def __init__(self, timestamp, message):
        self.timestamp = timestamp
        self.message = message


class NdtResult(object):
    """Represents the results of a complete NDT HTML5 client test.

    Attributes:
        start_time: The datetime at which tests were initiated (i.e. the time
            the driver pushed the 'Start Test' button).
        end_time: The datetime at which the tests completed (i.e. the time the
            results page loaded).
        c2s_start_time: The NdtSingleResult for the c2s (upload) test.
        s2c_start_time: The NdtSingleResult for the s2c (download) test.
        latency: The reported latency (in milliseconds).
        c2s_throughput: The reported upload (c2s) throughput (in kb/s).
        s2c_throughput: The reported download (s2c) throughput (in kb/s).
        errors: a list of TestError objects representing any errors encountered
            during the tests (or an empty list if all tests were successful).
    """

    def __init__(self,
                 start_time,
                 end_time,
                 c2s_start_time,
                 s2c_start_time,
                 errors,
                 latency=None,
                 c2s_throughput=None,
                 s2c_throughput=None):
        self.start_time = start_time
        self.end_time = end_time
        self.c2s_start_time = c2s_start_time
        self.s2c_start_time = s2c_start_time
        self.errors = errors
        self.latency = latency
        self.c2s_throughput = c2s_throughput
        self.s2c_throughput = s2c_throughput

    def __str__(self):
        return 'NDT Results:\n Start Time: %s,\n End Time: %s'\
        ',\n Latency: %s, \nErrors: %s' % (
            self.start_time, self.end_time, self.latency, self.errors)


class NdtHtml5SeleniumDriver(object):

    def perform_test(self, url, browser, timeout):
        """Performs an NDT test with the HTML5 client in the specified browser.

        Performs a full NDT test (both s2c and c2s) using the specified
        browser.

        Args:
            url: The URL of an NDT server to test against.
            browser: Can be one of 'firefox', 'chrome', 'edge', or 'safari'.
            timeout: The number of seconds that the driver will wait for
                each element to become visible before timing out.

        Returns:
            A populated NdtResult object
        """
        _result_values = {'start_time': None,
                               'end_time': None,
                               'c2s_start_time': None,
                               's2c_start_time': None,
                               'errors': []}
        driver = _create_browser(browser)
        try:
            driver.get(url)
        except WebDriverException as e:
            if e.msg == u'Target URL invalid_url is not well-formed.':
                _result_values['errors'].append(TestError(
                    datetime.now(pytz.utc), e.msg))
                driver.close()
                return NdtResult(**_result_values)
        driver.find_element_by_id('websocketButton').click()

        start_button = driver.find_elements_by_xpath(
            "//*[contains(text(), 'Start Test')]")[0]
        start_button.click()
        _result_values['start_time'] = datetime.now(pytz.utc)

        try:
            _result_values = _record_test_in_progress_values(_result_values, driver,
                timeout)

            _result_values = _populate_metric_values(_result_values, driver)

        except TimeoutException as e:
            message = 'Test did not complete within timeout period.'
            _result_values['errors'].append(TestError(
                datetime.now(pytz.utc), message))
            driver.close()
            return NdtResult(**_result_values)
        _result_values = _check_result_metrics(_result_values)

        driver.close()

        return NdtResult(**_result_values)


def _create_browser(browser):
    """Sets browser for an NDT test.

    Args:
        browser: Can be one of 'firefox', 'chrome', 'edge', or 'safari'

    Returns: An instance of a Selenium webdriver browser class
        corresponding to the specified browser.
    """
    if browser == 'firefox':
        return webdriver.Firefox()
    if browser in ['chrome', 'edge', 'safari']:
        raise NotImplementedError
    raise ValueError

def _record_test_in_progress_values(_result_values, driver, timeout):
    """Records values that are measured while the NDT test is in progress.

    Measures `s2c_start_time`, `c2s_end_time`, and `end_time`, which are
    stored in `_result_values`. These times are measured while the NDT test is in
    progress.

    Args:
        `driver`: An instance of a Selenium webdriver browser class.
        `_result_values`: A dictionary that stores the results of the NDT test.
        `timeout`: The number of seconds that the driver will wait for
            each element to become visible before timing out.

    Returns:
        `_result_values`
    """
    # wait until 'Now Testing your upload speed' is displayed
    upload_speed_text = driver.find_elements_by_xpath(
        "//*[contains(text(), 'your upload speed')]")[0]
    ui.WebDriverWait(
        driver,
        timeout=timeout).until(EC.visibility_of(upload_speed_text))
    _result_values['c2s_start_time'] = datetime.now(pytz.utc)

    # wait until 'Now Testing your download speed' is displayed
    download_speed_text = driver.find_elements_by_xpath(
        "//*[contains(text(), 'your download speed')]")[0]
    ui.WebDriverWait(
        driver,
        timeout=timeout).until(EC.visibility_of(download_speed_text))
    _result_values['s2c_start_time'] = datetime.now(pytz.utc)

    # wait until the results page appears
    results_text = driver.find_element_by_id('results')
    ui.WebDriverWait(
        driver,
        timeout=timeout).until(EC.visibility_of(results_text))
    _result_values['end_time'] = datetime.now(pytz.utc)
    return _result_values


def _populate_metric_values(_result_values, driver):
    """Populates _result_values with metrics from page.

    Args:
        driver: An instance of a Selenium webdriver browser class.
        _result_values:  A dictionary that stores the results of the NDT test.

    Returns:
        _result_values
    """
    _result_values['c2s_throughput'] = driver.find_element_by_id(
        'upload-speed').text
    _result_values['s2c_throughput'] = driver.find_element_by_id(
        'download-speed').text
    _result_values['latency'] = driver.find_element_by_id('latency').text
    return _result_values

def _check_result_metrics(_result_values):
    """Checks metric values in a result_values dict.

    Checks that the values for upload (c2s) throughput, download (s2c)
    throughput, and latency within the result_values dict are valid.

    Args:
        _result_values:  A dictionary that stores the results of the NDT test.

    Returns:
        _result_values
    """
    _result_values = _test_indiv_metric_is_valid(_result_values, 'latency')
    _result_values = _test_indiv_metric_is_valid(_result_values, 's2c_throughput')
    _result_values = _test_indiv_metric_is_valid(_result_values, 'c2s_throughput')
    return _result_values

def _test_indiv_metric_is_valid(_result_values, metric):
    """Checks whether a given metric is a valid numeric value.

    For a given metric in _result_values, checks that it is a valid numeric
    value. If not, an error is added to _result_values' errors list.

    Args:
        _result_values: A dictionary that stores the results of the NDT test.
        metric: One of 'latency', 's2c_throughput', or
            'c2s_throughput'.

    Returns:
        _result_values
    """
    try:
        float(_result_values[metric])
    except ValueError:
        message = 'illegal value shown for ' + metric + ': ' + \
            str(_result_values[metric])
        _result_values['errors'].append(TestError(
            datetime.now(pytz.utc), message))
    return _result_values



def main():
    selenium_driver = NdtHtml5SeleniumDriver()
    test_results = selenium_driver.perform_test(
        url='http://ndt.iupui.mlab4.nuq1t.measurement-lab.org:7123/',
        browser='firefox', timeout=20)
    print(test_results)


if __name__ == '__main__':
    main()
