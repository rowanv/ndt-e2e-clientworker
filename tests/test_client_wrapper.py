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
from __future__ import absolute_import
import unittest
import mock
from client_wrapper import client_wrapper
import selenium.webdriver.support.expected_conditions as selenium_expected_conditions
from selenium.common.exceptions import TimeoutException, WebDriverException


class ClientWrapperTimeoutTest(unittest.TestCase):

    def setUp(self):
        self.mock_driver = mock.patch.object(client_wrapper.webdriver,
                                             'Firefox',
                                             autospec=True)
        self.addCleanup(self.mock_driver.stop)
        self.mock_driver.start()

        self.mock_visibility = mock.patch.object(selenium_expected_conditions,
                                                 'visibility_of',
                                                 autospec=True)
        self.addCleanup(self.mock_visibility.stop)
        self.mock_visibility.start()
        self.mock_visibility.return_value = True

    def test_timeout_throws_error(self):
        # Call to webdriverwait throws timeout exception
        mock_web_driver_wait = mock.patch.object(client_wrapper.ui,
                                                 'WebDriverWait',
                                                 side_effect=TimeoutException,
                                                 autospec=True)
        mock_web_driver_wait.start()
        selenium_driver = client_wrapper.NdtHtml5SeleniumDriver()
        test_results = selenium_driver.perform_test(
            url='http://ndt.iupui.mlab4.nuq1t.measurement-lab.org:7123/',
            browser='firefox',
            timeout_time=1)

        mock_web_driver_wait.stop()
        # We have one error
        self.assertEqual(len(test_results.errors), 1)

        # And that is a timout error
        self.assertEqual(test_results.errors[0].message,
                         'Test did not complete within timeout period.')


class ClientWrapperCustomClassTest(unittest.TestCase):

    def setUp(self):
        self.mock_visibility = mock.patch.object(selenium_expected_conditions,
                                                 'visibility_of',
                                                 autospec=True)
        self.addCleanup(self.mock_visibility.stop)
        self.mock_visibility.return_value = True
        self.mock_visibility.start()

    def test_results_page_displays_non_numeric_metrics(self):
        """
        When latency, c2s_throughput, and s2c_throughput are non-numeric values,
        corresponding error objects are added to the errors list that indicate
        that each of these values is invalid.
        """

        # We patch selenium's web driver so it always has a non numeric
        # value as a WebElement.text attribute
        class NewWebElement(object):

            def __init__(self):
                self.text = 'Non numeric value'

            def click(self):
                pass

        class NewDriver(object):

            def get(self, url):
                pass

            def close(self):
                pass

            def find_element_by_id(self, id):
                return NewWebElement()

            def find_elements_by_xpath(self, xpath):
                return [NewWebElement()]

        self.mock_driver = mock.patch.object(client_wrapper.webdriver,
                                             'Firefox',
                                             autospec=True,
                                             return_value=NewDriver())
        self.mock_driver.start()

        selenium_driver = client_wrapper.NdtHtml5SeleniumDriver()
        test_results = selenium_driver.perform_test(
            url='http://ndt.iupui.mlab4.nuq1t.measurement-lab.org:7123/',
            browser='firefox',
            timeout_time=1000)

        # And the appropriate error objects are contained in
        # the list
        self.assertEqual(test_results.errors[0].message,
                         'illegal value shown for latency: Non numeric value')
        self.assertEqual(
            test_results.errors[1].message,
            'illegal value shown for s2c_throughput: Non numeric value')
        self.assertEqual(
            test_results.errors[2].message,
            'illegal value shown for c2s_throughput: Non numeric value')

        self.mock_driver.stop()

    def test_results_page_displays_numeric_latency(self):
        """
        When latency is a numeric value, an error object is not added to the
        errors list.
        """

        # Mock so always returns a numeric value for a WebElement.text attribute
        class NewWebElement(object):

            def __init__(self):
                self.text = '72'

            def click(self):
                pass

        class NewDriver(object):

            def get(self, url):
                pass

            def close(self):
                pass

            def find_element_by_id(self, id):
                return NewWebElement()

            def find_elements_by_xpath(self, xpath):
                return [NewWebElement()]

        self.mock_driver = mock.patch.object(client_wrapper.webdriver,
                                             'Firefox',
                                             autospec=True,
                                             return_value=NewDriver())

        self.mock_driver.start()

        selenium_driver = client_wrapper.NdtHtml5SeleniumDriver()
        test_results = selenium_driver.perform_test(
            url='http://ndt.iupui.mlab4.nuq1t.measurement-lab.org:7123/',
            browser='firefox',
            timeout_time=1000)
        self.assertEqual(test_results.latency, '72')
        # And an error object is not contained in the list
        self.assertEqual(len(test_results.errors), 0)

        self.mock_driver.stop()


class ClientWrapperInvalidURLTest(unittest.TestCase):

    def test_invalid_URL_throws_error(self):

        # Mock calls to driver.get() so that a WebDriverException is always raised
        class NewDriver(object):

            def get(self, url):
                raise WebDriverException(
                    u'Target URL invalid_url is not well-formed.')

            def close(self):
                pass

        mock_driver = mock.patch.object(client_wrapper.webdriver,
                                        'Firefox',
                                        return_value=NewDriver())
        mock_driver.start()
        selenium_driver = client_wrapper.NdtHtml5SeleniumDriver()
        test_results = selenium_driver.perform_test(url='invalid_url',
                                                    browser='firefox',
                                                    timeout_time=1)
        mock_driver.stop()

        # We have one error
        self.assertEqual(len(test_results.errors), 1)

        # And that error is about the test results URL not being
        # well-formed
        self.assertEqual(test_results.errors[0].message,
                         u'Target URL invalid_url is not well-formed.')


if __name__ == '__main__':
    unittest.main()
