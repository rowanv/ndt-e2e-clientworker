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


class NdtSingleTestResult(object):
    """Result of a single NDT test.

    Attributes:
        throughput: The final recorded throughput (in Mbps).
        start_time: The datetime when the test began (or None if the test
            never began).
        end_time: The datetime when the test competed (or None if the test
            never completed).
    """

    def __init__(self, throughput=None, start_time=None, end_time=None):
        self.throughput = throughput
        self.start_time = start_time
        self.end_time = end_time


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
        c2s_result: The NdtSingleResult for the c2s (upload) test.
        s2c_result: The NdtSingleResult for the s2c (download) test.
        latency: The reported latency (in milliseconds).
        errors: a list of TestError objects representing any errors encountered
            during the tests (or an empty list if all tests were successful).
    """

    def __init__(self,
                 start_time,
                 end_time,
                 errors,
                 c2s_result=None,
                 s2c_result=None,
                 latency=None):
        self.start_time = start_time
        self.end_time = end_time
        self.c2s_result = c2s_result
        self.s2c_result = s2c_result
        self.errors = errors
        self.latency = latency

    def __str__(self):
        return 'NDT Results:\n Start Time: %s,\n End Time: %s'\
        ',\n Latency: %s, \nErrors: %s' % (
            self.start_time, self.end_time, self.latency, self.errors)
