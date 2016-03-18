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

import os
import sys
import unittest

sys.path.insert(1, os.path.abspath(os.path.join(
    os.path.dirname(__file__), '../client_wrapper')))
import foo


class ClientWrapperTest(unittest.TestCase):

    def test_run_tests_executes_all_tests_successfully(self):
        """Dummy test to exercise CI setup, not permanent."""
        self.assertTrue(foo.bar())


if __name__ == '__main__':
    unittest.main()
