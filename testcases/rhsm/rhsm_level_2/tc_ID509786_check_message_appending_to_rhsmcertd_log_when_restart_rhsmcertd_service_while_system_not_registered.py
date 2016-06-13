"""
@author        : qianzhan@redhat.com
@date        : 2016-06-13
"""

from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509786_check_message_appending_to_rhsmcertd_log_when_restart_rhsmcertd_service_while_system_not_registered(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # Unregister and clean
            self.restore_environment()

            # Set certFrequency=1 and restart rhsmcertd
            self.set_auto_attach_interval(1)

            # remove current content of rhsm.log
            cmd = 'echo "" /var/log/rhsm/rhsm.log'
            (ret, output) = self.runcmd(cmd, "remove rhsm.log")
            if ret == 0:
                logger.info("It's successful to remove rhsm.log")
            else:
                raise FailException("Test Failed - Failed to remove rhsm.log")

            self.restart_rhsmcertd()
            
            # Check rhsm.log message
            message1="\'Either the consumer is not registered or the certificates are corrupted. Certificate update using daemon failed.'"
            message2="\'certificates updated\'"
            
            cmd = "grep %s /var/log/rhsm/rhsm.log"%message1
            (ret, output) = self.runcmd(cmd, "check rhsm.log")
            if ret == 0:
                logger.info("It's successful to check rhsm.log message1")
            else:
                raise FailException("Test Failed - Failed to check rhsm.log message1")

            cmd = "grep %s /var/log/rhsm/rhsm.log"%message2
            (ret, output) = self.runcmd(cmd, "check rhsm.log")
            if ret != 0:
                logger.info("It's successful to check rhsm.log message2")
            else:
                raise FailException("Test Failed - Failed to check rhsm.log message2")

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            # Restore the default auto-attach interval as 1440
            self.set_auto_attach_interval(1440)
            self.restart_rhsmcertd()
            if self.check_auto_attach_interval() == '1440.0':
                logger.info("It's successful to restore auto-attach interval")
            else:
                raise FailException("Test Failed - Failed to  restore auto-attach interval")
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)



if __name__ == "__main__":
    unittest.main()
