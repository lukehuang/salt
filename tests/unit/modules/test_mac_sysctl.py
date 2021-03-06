# -*- coding: utf-8 -*-
'''
    :codeauthor: :email:`Nicole Thomas <nicole@saltstack.com>`
'''

# Import Python libs
from __future__ import absolute_import

# Import Salt Libs
import salt.modules.mac_sysctl as mac_sysctl
from salt.exceptions import CommandExecutionError

# Import Salt Testing Libs
from tests.support.mixins import LoaderModuleMockMixin
from tests.support.unit import skipIf, TestCase
from tests.support.mock import (
    MagicMock,
    mock_open,
    patch,
    call,
    NO_MOCK,
    NO_MOCK_REASON
)


@skipIf(NO_MOCK, NO_MOCK_REASON)
class DarwinSysctlTestCase(TestCase, LoaderModuleMockMixin):
    '''
    TestCase for salt.modules.mac_sysctl module
    '''
    def setup_loader_modules(self):
        return {mac_sysctl: {}}

    def test_get(self):
        '''
        Tests the return of get function
        '''
        mock_cmd = MagicMock(return_value='foo')
        with patch.dict(mac_sysctl.__salt__, {'cmd.run': mock_cmd}):
            self.assertEqual(mac_sysctl.get('kern.ostype'), 'foo')

    def test_assign_cmd_failed(self):
        '''
        Tests if the assignment was successful or not
        '''
        cmd = {'pid': 3548, 'retcode': 1, 'stderr': '',
               'stdout': 'net.inet.icmp.icmplim: 250 -> 50'}
        mock_cmd = MagicMock(return_value=cmd)
        with patch.dict(mac_sysctl.__salt__, {'cmd.run_all': mock_cmd}):
            self.assertRaises(CommandExecutionError,
                              mac_sysctl.assign,
                              'net.inet.icmp.icmplim', 50)

    def test_assign(self):
        '''
        Tests the return of successful assign function
        '''
        cmd = {'pid': 3548, 'retcode': 0, 'stderr': '',
               'stdout': 'net.inet.icmp.icmplim: 250 -> 50'}
        ret = {'net.inet.icmp.icmplim': '50'}
        mock_cmd = MagicMock(return_value=cmd)
        with patch.dict(mac_sysctl.__salt__, {'cmd.run_all': mock_cmd}):
            self.assertEqual(mac_sysctl.assign(
                'net.inet.icmp.icmplim', 50), ret)

    def test_persist_no_conf_failure(self):
        '''
        Tests adding of config file failure
        '''
        with patch('salt.utils.fopen', mock_open()) as m_open, \
                patch('os.path.isfile', MagicMock(return_value=False)):
            m_open.side_effect = IOError(13, 'Permission denied', '/file')
            self.assertRaises(CommandExecutionError,
                              mac_sysctl.persist,
                              'net.inet.icmp.icmplim',
                              50, config=None)

    def test_persist_no_conf_success(self):
        '''
        Tests successful add of config file when previously not one
        '''
        with patch('salt.utils.fopen', mock_open()) as m_open, \
                patch('os.path.isfile', MagicMock(return_value=False)):
            mac_sysctl.persist('net.inet.icmp.icmplim', 50)
            helper_open = m_open()
            helper_open.write.assert_called_once_with(
                '#\n# Kernel sysctl configuration\n#\n')

    def test_persist_success(self):
        '''
        Tests successful write to existing sysctl file
        '''
        to_write = '#\n# Kernel sysctl configuration\n#\n'
        m_calls_list = [call.writelines(['net.inet.icmp.icmplim=50', '\n'])]
        with patch('salt.utils.fopen', mock_open(read_data=to_write)) as m_open, \
                patch('os.path.isfile', MagicMock(return_value=True)):
            mac_sysctl.persist('net.inet.icmp.icmplim', 50, config=to_write)
            helper_open = m_open()
            calls_list = helper_open.method_calls
            self.assertEqual(calls_list, m_calls_list)
