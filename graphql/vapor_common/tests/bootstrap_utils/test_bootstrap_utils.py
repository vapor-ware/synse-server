#!/usr/bin/env python
""" Tests for Vapor Common's Bootstrap Utils

    Author: Erick Daniszewski
    Date:   11 Dec 2016
    
    \\//
     \/apor IO
"""
import unittest
import os

from vapor_common.utils import bootstrap
from vapor_common.variables import VAPOR_EXEC_MODE, VAPOR_BOOTSTRAP_BLOCK


class BootstrapUtilTestCase(unittest.TestCase):

    def test_000_has_execution_mode(self):
        """ Test checking the execution mode when no ENV variable is set.

        In this case, the mode 'ipmi' is tested.
        """
        self.assertIsNone(os.getenv(VAPOR_EXEC_MODE))

        ret = bootstrap.has_execution_mode('ipmi')
        self.assertFalse(ret)

        self.assertIsNone(os.getenv(VAPOR_EXEC_MODE))

    def test_001_has_execution_mode(self):
        """ Test checking the execution mode when no ENV variable is set.

        In this case, the mode 'ipmi' is tested (in upper case).
        """
        self.assertIsNone(os.getenv(VAPOR_EXEC_MODE))

        ret = bootstrap.has_execution_mode('IPMI')
        self.assertFalse(ret)

        self.assertIsNone(os.getenv(VAPOR_EXEC_MODE))

    def test_002_has_execution_mode(self):
        """ Test checking the execution mode when no ENV variable is set.

        In this case, the mode 'ipmi' is tested (in mixed case).
        """
        self.assertIsNone(os.getenv(VAPOR_EXEC_MODE))

        ret = bootstrap.has_execution_mode('IpMi')
        self.assertFalse(ret)

        self.assertIsNone(os.getenv(VAPOR_EXEC_MODE))

    def test_003_has_execution_mode(self):
        """ Test checking the execution mode when no ENV variable is set.

        In this case, the mode 'chamber' is tested.
        """
        self.assertIsNone(os.getenv(VAPOR_EXEC_MODE))

        ret = bootstrap.has_execution_mode('chamber')
        self.assertFalse(ret)

        self.assertIsNone(os.getenv(VAPOR_EXEC_MODE))

    def test_004_has_execution_mode(self):
        """ Test checking the execution mode when no ENV variable is set.

        In this case, the mode 'chamber' is tested (in upper case).
        """
        self.assertIsNone(os.getenv(VAPOR_EXEC_MODE))

        ret = bootstrap.has_execution_mode('CHAMBER')
        self.assertFalse(ret)

        self.assertIsNone(os.getenv(VAPOR_EXEC_MODE))

    def test_005_has_execution_mode(self):
        """ Test checking the execution mode when no ENV variable is set.

        In this case, the mode 'chamber' is tested (in mixed case).
        """
        self.assertIsNone(os.getenv(VAPOR_EXEC_MODE))

        ret = bootstrap.has_execution_mode('ChAmBeR')
        self.assertFalse(ret)

        self.assertIsNone(os.getenv(VAPOR_EXEC_MODE))

    def test_006_has_execution_mode(self):
        """ Test checking the execution mode when no ENV variable is set.

        In this case, an empty mode string is tested.
        """
        self.assertIsNone(os.getenv(VAPOR_EXEC_MODE))

        ret = bootstrap.has_execution_mode('')
        self.assertFalse(ret)

        self.assertIsNone(os.getenv(VAPOR_EXEC_MODE))

    def test_007_has_execution_mode(self):
        """ Test checking the execution mode when no ENV variable is set.

        In this case, an unsupported mode string is tested.
        """
        self.assertIsNone(os.getenv(VAPOR_EXEC_MODE))

        ret = bootstrap.has_execution_mode('not-a-mode')
        self.assertFalse(ret)

        self.assertIsNone(os.getenv(VAPOR_EXEC_MODE))

    def test_008_has_execution_mode(self):
        """ Test checking the execution mode when the ENV variable is set
        for IPMI mode.

        In this case, the mode 'ipmi' is tested.
        """
        os.environ[VAPOR_EXEC_MODE] = 'ipmi'
        self.assertEqual(os.getenv(VAPOR_EXEC_MODE), 'ipmi')

        ret = bootstrap.has_execution_mode('ipmi')
        self.assertTrue(ret)

        self.assertEqual(os.getenv(VAPOR_EXEC_MODE), 'ipmi')

    def test_009_has_execution_mode(self):
        """ Test checking the execution mode when the ENV variable is set
        for IPMI mode.

        In this case, the mode 'ipmi' is tested (in upper case).
        """
        os.environ[VAPOR_EXEC_MODE] = 'ipmi'
        self.assertEqual(os.getenv(VAPOR_EXEC_MODE), 'ipmi')

        ret = bootstrap.has_execution_mode('IPMI')
        self.assertTrue(ret)

        self.assertEqual(os.getenv(VAPOR_EXEC_MODE), 'ipmi')

    def test_010_has_execution_mode(self):
        """ Test checking the execution mode when the ENV variable is set
        for IPMI mode.

        In this case, the mode 'ipmi' is tested (in mixed case).
        """
        os.environ[VAPOR_EXEC_MODE] = 'ipmi'
        self.assertEqual(os.getenv(VAPOR_EXEC_MODE), 'ipmi')

        ret = bootstrap.has_execution_mode('IpMi')
        self.assertTrue(ret)

        self.assertEqual(os.getenv(VAPOR_EXEC_MODE), 'ipmi')

    def test_011_has_execution_mode(self):
        """ Test checking the execution mode when the ENV variable is set
        for IPMI mode.

        In this case, the mode 'chamber' is tested.
        """
        os.environ[VAPOR_EXEC_MODE] = 'ipmi'
        self.assertEqual(os.getenv(VAPOR_EXEC_MODE), 'ipmi')

        ret = bootstrap.has_execution_mode('chamber')
        self.assertFalse(ret)

        self.assertEqual(os.getenv(VAPOR_EXEC_MODE), 'ipmi')

    def test_012_has_execution_mode(self):
        """ Test checking the execution mode when the ENV variable is set
        for IPMI mode.

        In this case, the mode 'chamber' is tested (in upper case).
        """
        os.environ[VAPOR_EXEC_MODE] = 'ipmi'
        self.assertEqual(os.getenv(VAPOR_EXEC_MODE), 'ipmi')

        ret = bootstrap.has_execution_mode('CHAMBER')
        self.assertFalse(ret)

        self.assertEqual(os.getenv(VAPOR_EXEC_MODE), 'ipmi')

    def test_013_has_execution_mode(self):
        """ Test checking the execution mode when the ENV variable is set
        for IPMI mode.

        In this case, the mode 'chamber' is tested (in mixed case).
        """
        os.environ[VAPOR_EXEC_MODE] = 'ipmi'
        self.assertEqual(os.getenv(VAPOR_EXEC_MODE), 'ipmi')

        ret = bootstrap.has_execution_mode('ChAmBeR')
        self.assertFalse(ret)

        self.assertEqual(os.getenv(VAPOR_EXEC_MODE), 'ipmi')

    def test_014_has_execution_mode(self):
        """ Test checking the execution mode when the ENV variable is set
        for IPMI mode.

        In this case, an empty mode string is tested.
        """
        os.environ[VAPOR_EXEC_MODE] = 'ipmi'
        self.assertEqual(os.getenv(VAPOR_EXEC_MODE), 'ipmi')

        ret = bootstrap.has_execution_mode('')
        self.assertFalse(ret)

        self.assertEqual(os.getenv(VAPOR_EXEC_MODE), 'ipmi')

    def test_015_has_execution_mode(self):
        """ Test checking the execution mode when the ENV variable is set
        for IPMI mode.

        In this case, an unsupported mode string is tested.
        """
        os.environ[VAPOR_EXEC_MODE] = 'ipmi'
        self.assertEqual(os.getenv(VAPOR_EXEC_MODE), 'ipmi')

        ret = bootstrap.has_execution_mode('not-a-mode')
        self.assertFalse(ret)

        self.assertEqual(os.getenv(VAPOR_EXEC_MODE), 'ipmi')

    def test_016_has_execution_mode(self):
        """ Test checking the execution mode when the ENV variable is set
        for Chamber mode.

        In this case, the mode 'ipmi' is tested.
        """
        os.environ[VAPOR_EXEC_MODE] = 'chamber'
        self.assertEqual(os.getenv(VAPOR_EXEC_MODE), 'chamber')

        ret = bootstrap.has_execution_mode('ipmi')
        self.assertFalse(ret)

        self.assertEqual(os.getenv(VAPOR_EXEC_MODE), 'chamber')

    def test_017_has_execution_mode(self):
        """ Test checking the execution mode when the ENV variable is set
        for Chamber mode.

        In this case, the mode 'ipmi' is tested (in upper case).
        """
        os.environ[VAPOR_EXEC_MODE] = 'chamber'
        self.assertEqual(os.getenv(VAPOR_EXEC_MODE), 'chamber')

        ret = bootstrap.has_execution_mode('IPMI')
        self.assertFalse(ret)

        self.assertEqual(os.getenv(VAPOR_EXEC_MODE), 'chamber')

    def test_018_has_execution_mode(self):
        """ Test checking the execution mode when the ENV variable is set
        for Chamber mode.

        In this case, the mode 'ipmi' is tested (in mixed case).
        """
        os.environ[VAPOR_EXEC_MODE] = 'chamber'
        self.assertEqual(os.getenv(VAPOR_EXEC_MODE), 'chamber')

        ret = bootstrap.has_execution_mode('IpMi')
        self.assertFalse(ret)

        self.assertEqual(os.getenv(VAPOR_EXEC_MODE), 'chamber')

    def test_019_has_execution_mode(self):
        """ Test checking the execution mode when the ENV variable is set
        for Chamber mode.

        In this case, the mode 'chamber' is tested.
        """
        os.environ[VAPOR_EXEC_MODE] = 'chamber'
        self.assertEqual(os.getenv(VAPOR_EXEC_MODE), 'chamber')

        ret = bootstrap.has_execution_mode('chamber')
        self.assertTrue(ret)

        self.assertEqual(os.getenv(VAPOR_EXEC_MODE), 'chamber')

    def test_020_has_execution_mode(self):
        """ Test checking the execution mode when the ENV variable is set
        for Chamber mode.

        In this case, the mode 'chamber' is tested (in upper case).
        """
        os.environ[VAPOR_EXEC_MODE] = 'chamber'
        self.assertEqual(os.getenv(VAPOR_EXEC_MODE), 'chamber')

        ret = bootstrap.has_execution_mode('CHAMBER')
        self.assertTrue(ret)

        self.assertEqual(os.getenv(VAPOR_EXEC_MODE), 'chamber')

    def test_021_has_execution_mode(self):
        """ Test checking the execution mode when the ENV variable is set
        for Chamber mode.

        In this case, the mode 'chamber' is tested (in mixed case).
        """
        os.environ[VAPOR_EXEC_MODE] = 'chamber'
        self.assertEqual(os.getenv(VAPOR_EXEC_MODE), 'chamber')

        ret = bootstrap.has_execution_mode('ChAmBeR')
        self.assertTrue(ret)

        self.assertEqual(os.getenv(VAPOR_EXEC_MODE), 'chamber')

    def test_022_has_execution_mode(self):
        """ Test checking the execution mode when the ENV variable is set
        for Chamber mode.

        In this case, an empty mode string is tested.
        """
        os.environ[VAPOR_EXEC_MODE] = 'chamber'
        self.assertEqual(os.getenv(VAPOR_EXEC_MODE), 'chamber')

        ret = bootstrap.has_execution_mode('')
        self.assertFalse(ret)

        self.assertEqual(os.getenv(VAPOR_EXEC_MODE), 'chamber')

    def test_023_has_execution_mode(self):
        """ Test checking the execution mode when the ENV variable is set
        for Chamber mode.

        In this case, an unsupported mode string is tested.
        """
        os.environ[VAPOR_EXEC_MODE] = 'chamber'
        self.assertEqual(os.getenv(VAPOR_EXEC_MODE), 'chamber')

        ret = bootstrap.has_execution_mode('not-a-mode')
        self.assertFalse(ret)

        self.assertEqual(os.getenv(VAPOR_EXEC_MODE), 'chamber')

    def test_024_get_bootstrap_block_state(self):
        """ Test getting the bootstrap block state when the ENV variable is
        not set.

        In this case, we expect the default values to be returned, indicating
        that blocking mode is enabled.
        """
        self.assertIsNone(os.getenv(VAPOR_BOOTSTRAP_BLOCK))

        ret = bootstrap.get_bootstrap_block_state()
        self.assertIsInstance(ret, tuple)

        timeout, delay, retry = ret
        self.assertEqual(timeout, None)
        self.assertEqual(delay, 2)
        self.assertEqual(retry, None)

        self.assertIsNone(os.getenv(VAPOR_BOOTSTRAP_BLOCK))

    def test_025_get_bootstrap_block_state(self):
        """ Test getting the bootstrap block state when the ENV variable is
        set to 'True'.

        In this case, we expect the default values to be returned, indicating
        that blocking mode is enabled.
        """
        os.environ[VAPOR_BOOTSTRAP_BLOCK] = 'True'
        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), 'True')

        ret = bootstrap.get_bootstrap_block_state()
        self.assertIsInstance(ret, tuple)

        timeout, delay, retry = ret
        self.assertEqual(timeout, None)
        self.assertEqual(delay, 2)
        self.assertEqual(retry, None)

        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), 'True')

    def test_026_get_bootstrap_block_state(self):
        """ Test getting the bootstrap block state when the ENV variable is
        set to 'true'.

        In this case, we expect the default values to be returned, indicating
        that blocking mode is enabled.
        """
        os.environ[VAPOR_BOOTSTRAP_BLOCK] = 'true'
        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), 'true')

        ret = bootstrap.get_bootstrap_block_state()
        self.assertIsInstance(ret, tuple)

        timeout, delay, retry = ret
        self.assertEqual(timeout, None)
        self.assertEqual(delay, 2)
        self.assertEqual(retry, None)

        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), 'true')

    def test_027_get_bootstrap_block_state(self):
        """ Test getting the bootstrap block state when the ENV variable is
        set to 'block'.

        In this case, we expect the default values to be returned, indicating
        that blocking mode is enabled.
        """
        os.environ[VAPOR_BOOTSTRAP_BLOCK] = 'block'
        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), 'block')

        ret = bootstrap.get_bootstrap_block_state()
        self.assertIsInstance(ret, tuple)

        timeout, delay, retry = ret
        self.assertEqual(timeout, None)
        self.assertEqual(delay, 2)
        self.assertEqual(retry, None)

        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), 'block')

    def test_028_get_bootstrap_block_state(self):
        """ Test getting the bootstrap block state when the ENV variable is
        set to some value which will fall through to the default.

        In this case, we expect the default values to be returned, indicating
        that blocking mode is enabled.
        """
        os.environ[VAPOR_BOOTSTRAP_BLOCK] = 'some-unspecific-value'
        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), 'some-unspecific-value')

        ret = bootstrap.get_bootstrap_block_state()
        self.assertIsInstance(ret, tuple)

        timeout, delay, retry = ret
        self.assertEqual(timeout, None)
        self.assertEqual(delay, 2)
        self.assertEqual(retry, None)

        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), 'some-unspecific-value')

    def test_029_get_bootstrap_block_state(self):
        """ Test getting the bootstrap block state when the ENV variable is
        set to '0'.

        In this case, we take this to mean that blocking should be disabled.
        """
        os.environ[VAPOR_BOOTSTRAP_BLOCK] = '0'
        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), '0')

        ret = bootstrap.get_bootstrap_block_state()
        self.assertIsInstance(ret, tuple)

        timeout, delay, retry = ret
        self.assertEqual(timeout, 1)
        self.assertEqual(delay, 2)
        self.assertEqual(retry, 1)

        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), '0')

    def test_030_get_bootstrap_block_state(self):
        """ Test getting the bootstrap block state when the ENV variable is
        set to '0.0'.

        In this case, we take this to mean that blocking should be disabled.
        """
        os.environ[VAPOR_BOOTSTRAP_BLOCK] = '0.0'
        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), '0.0')

        ret = bootstrap.get_bootstrap_block_state()
        self.assertIsInstance(ret, tuple)

        timeout, delay, retry = ret
        self.assertEqual(timeout, 1)
        self.assertEqual(delay, 2)
        self.assertEqual(retry, 1)

        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), '0.0')

    def test_031_get_bootstrap_block_state(self):
        """ Test getting the bootstrap block state when the ENV variable is
        set to 'false'.

        In this case, we take this to mean that blocking should be disabled.
        """
        os.environ[VAPOR_BOOTSTRAP_BLOCK] = 'false'
        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), 'false')

        ret = bootstrap.get_bootstrap_block_state()
        self.assertIsInstance(ret, tuple)

        timeout, delay, retry = ret
        self.assertEqual(timeout, 1)
        self.assertEqual(delay, 2)
        self.assertEqual(retry, 1)

        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), 'false')

    def test_032_get_bootstrap_block_state(self):
        """ Test getting the bootstrap block state when the ENV variable is
        set to 'False'.

        In this case, we take this to mean that blocking should be disabled.
        """
        os.environ[VAPOR_BOOTSTRAP_BLOCK] = 'False'
        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), 'False')

        ret = bootstrap.get_bootstrap_block_state()
        self.assertIsInstance(ret, tuple)

        timeout, delay, retry = ret
        self.assertEqual(timeout, 1)
        self.assertEqual(delay, 2)
        self.assertEqual(retry, 1)

        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), 'False')

    def test_033_get_bootstrap_block_state(self):
        """ Test getting the bootstrap block state when the ENV variable is
        set to 'none'.

        In this case, we take this to mean that blocking should be disabled.
        """
        os.environ[VAPOR_BOOTSTRAP_BLOCK] = 'none'
        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), 'none')

        ret = bootstrap.get_bootstrap_block_state()
        self.assertIsInstance(ret, tuple)

        timeout, delay, retry = ret
        self.assertEqual(timeout, 1)
        self.assertEqual(delay, 2)
        self.assertEqual(retry, 1)

        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), 'none')

    def test_034_get_bootstrap_block_state(self):
        """ Test getting the bootstrap block state when the ENV variable is
        set to 'None'.

        In this case, we take this to mean that blocking should be disabled.
        """
        os.environ[VAPOR_BOOTSTRAP_BLOCK] = 'None'
        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), 'None')

        ret = bootstrap.get_bootstrap_block_state()
        self.assertIsInstance(ret, tuple)

        timeout, delay, retry = ret
        self.assertEqual(timeout, 1)
        self.assertEqual(delay, 2)
        self.assertEqual(retry, 1)

        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), 'None')

    def test_035_get_bootstrap_block_state(self):
        """ Test getting the bootstrap block state when the ENV variable is
        set to 'null'.

        In this case, we take this to mean that blocking should be disabled.
        """
        os.environ[VAPOR_BOOTSTRAP_BLOCK] = 'null'
        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), 'null')

        ret = bootstrap.get_bootstrap_block_state()
        self.assertIsInstance(ret, tuple)

        timeout, delay, retry = ret
        self.assertEqual(timeout, 1)
        self.assertEqual(delay, 2)
        self.assertEqual(retry, 1)

        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), 'null')

    def test_036_get_bootstrap_block_state(self):
        """ Test getting the bootstrap block state when the ENV variable is
        set to 'Null'.

        In this case, we take this to mean that blocking should be disabled.
        """
        os.environ[VAPOR_BOOTSTRAP_BLOCK] = 'Null'
        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), 'Null')

        ret = bootstrap.get_bootstrap_block_state()
        self.assertIsInstance(ret, tuple)

        timeout, delay, retry = ret
        self.assertEqual(timeout, 1)
        self.assertEqual(delay, 2)
        self.assertEqual(retry, 1)

        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), 'Null')

    def test_037_get_bootstrap_block_state(self):
        """ Test getting the bootstrap block state when the ENV variable is
        set to '1'.

        In this case, we take this to mean that blocking should be disabled.
        """
        os.environ[VAPOR_BOOTSTRAP_BLOCK] = '1'
        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), '1')

        ret = bootstrap.get_bootstrap_block_state()
        self.assertIsInstance(ret, tuple)

        timeout, delay, retry = ret
        self.assertEqual(timeout, 1)
        self.assertEqual(delay, 2)
        self.assertEqual(retry, 1)

        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), '1')

    def test_038_get_bootstrap_block_state(self):
        """ Test getting the bootstrap block state when the ENV variable is
        set to '1.0'.

        In this case, we take this to mean that blocking should be disabled.
        """
        os.environ[VAPOR_BOOTSTRAP_BLOCK] = '1.0'
        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), '1.0')

        ret = bootstrap.get_bootstrap_block_state()
        self.assertIsInstance(ret, tuple)

        timeout, delay, retry = ret
        self.assertEqual(timeout, 1)
        self.assertEqual(delay, 2)
        self.assertEqual(retry, 1)

        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), '1.0')

    def test_039_get_bootstrap_block_state(self):
        """ Test getting the bootstrap block state when the ENV variable is
        set to '8'.

        In this case, we take this to mean that blocking should be disabled.
        """
        os.environ[VAPOR_BOOTSTRAP_BLOCK] = '8'
        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), '8')

        ret = bootstrap.get_bootstrap_block_state()
        self.assertIsInstance(ret, tuple)

        timeout, delay, retry = ret
        self.assertEqual(timeout, 8)
        self.assertEqual(delay, 2)
        self.assertEqual(retry, 4)

        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), '8')

    def test_040_get_bootstrap_block_state(self):
        """ Test getting the bootstrap block state when the ENV variable is
        set to '8.0'.

        In this case, we take this to mean that blocking should be disabled.
        """
        os.environ[VAPOR_BOOTSTRAP_BLOCK] = '8.0'
        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), '8.0')

        ret = bootstrap.get_bootstrap_block_state()
        self.assertIsInstance(ret, tuple)

        timeout, delay, retry = ret
        self.assertEqual(timeout, 8)
        self.assertEqual(delay, 2)
        self.assertEqual(retry, 4)

        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), '8.0')

    def test_041_get_bootstrap_block_state(self):
        """ Test getting the bootstrap block state when the ENV variable is
        set to '11'.

        In this case, we take this to mean that blocking should be disabled.
        """
        os.environ[VAPOR_BOOTSTRAP_BLOCK] = '11'
        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), '11')

        ret = bootstrap.get_bootstrap_block_state()
        self.assertIsInstance(ret, tuple)

        timeout, delay, retry = ret
        self.assertEqual(timeout, 11)
        self.assertEqual(delay, 2)
        self.assertEqual(retry, 5)

        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), '11')

    def test_042_get_bootstrap_block_state(self):
        """ Test getting the bootstrap block state when the ENV variable is
        set to '11.0'.

        In this case, we take this to mean that blocking should be disabled.
        """
        os.environ[VAPOR_BOOTSTRAP_BLOCK] = '11.0'
        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), '11.0')

        ret = bootstrap.get_bootstrap_block_state()
        self.assertIsInstance(ret, tuple)

        timeout, delay, retry = ret
        self.assertEqual(timeout, 11)
        self.assertEqual(delay, 2)
        self.assertEqual(retry, 5)

        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), '11.0')

    def test_043_get_bootstrap_block_state(self):
        """ Test getting the bootstrap block state when the ENV variable is
        set to '3.5'.

        In this case, we take this to mean that blocking should be disabled.
        """
        os.environ[VAPOR_BOOTSTRAP_BLOCK] = '3.5'
        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), '3.5')

        ret = bootstrap.get_bootstrap_block_state()
        self.assertIsInstance(ret, tuple)

        timeout, delay, retry = ret
        self.assertEqual(timeout, 3.5)
        self.assertEqual(delay, 2)
        self.assertEqual(retry, 1)

        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), '3.5')

    def test_044_get_bootstrap_block_state(self):
        """ Test getting the bootstrap block state when the ENV variable is
        set to '-1'.

        In the case that a negative number is given, we resort to the default
        behavior of blocking.
        """
        os.environ[VAPOR_BOOTSTRAP_BLOCK] = '-1'
        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), '-1')

        ret = bootstrap.get_bootstrap_block_state()
        self.assertIsInstance(ret, tuple)

        timeout, delay, retry = ret
        self.assertEqual(timeout, None)
        self.assertEqual(delay, 2)
        self.assertEqual(retry, None)

        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), '-1')

    def test_045_get_bootstrap_block_state(self):
        """ Test getting the bootstrap block state when the ENV variable is
        set to '-1.0'.

        In the case that a negative number is given, we resort to the default
        behavior of blocking.
        """
        os.environ[VAPOR_BOOTSTRAP_BLOCK] = '-1.0'
        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), '-1.0')

        ret = bootstrap.get_bootstrap_block_state()
        self.assertIsInstance(ret, tuple)

        timeout, delay, retry = ret
        self.assertEqual(timeout, None)
        self.assertEqual(delay, 2)
        self.assertEqual(retry, None)

        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), '-1.0')

    def test_046_get_bootstrap_block_state(self):
        """ Test getting the bootstrap block state when the ENV variable is
        set to '-10'.

        In the case that a negative number is given, we resort to the default
        behavior of blocking.
        """
        os.environ[VAPOR_BOOTSTRAP_BLOCK] = '-10'
        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), '-10')

        ret = bootstrap.get_bootstrap_block_state()
        self.assertIsInstance(ret, tuple)

        timeout, delay, retry = ret
        self.assertEqual(timeout, None)
        self.assertEqual(delay, 2)
        self.assertEqual(retry, None)

        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), '-10')

    def test_047_get_bootstrap_block_state(self):
        """ Test getting the bootstrap block state when the ENV variable is
        set to '-10.0'.

        In the case that a negative number is given, we resort to the default
        behavior of blocking.
        """
        os.environ[VAPOR_BOOTSTRAP_BLOCK] = '-10.0'
        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), '-10.0')

        ret = bootstrap.get_bootstrap_block_state()
        self.assertIsInstance(ret, tuple)

        timeout, delay, retry = ret
        self.assertEqual(timeout, None)
        self.assertEqual(delay, 2)
        self.assertEqual(retry, None)

        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), '-10.0')

    def test_048_get_bootstrap_block_state(self):
        """ Test getting the bootstrap block state when the ENV variable is
        set to '-5.65'.

        In the case that a negative number is given, we resort to the default
        behavior of blocking.
        """
        os.environ[VAPOR_BOOTSTRAP_BLOCK] = '-5.65'
        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), '-5.65')

        ret = bootstrap.get_bootstrap_block_state()
        self.assertIsInstance(ret, tuple)

        timeout, delay, retry = ret
        self.assertEqual(timeout, None)
        self.assertEqual(delay, 2)
        self.assertEqual(retry, None)

        self.assertEqual(os.getenv(VAPOR_BOOTSTRAP_BLOCK), '-5.65')
