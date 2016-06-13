"""
@author        : qianzhan@redhat.com
@date        : 2016-05-25
"""

from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509492_enable_healing_feature(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # Enable healing via setting the auto-attach interval as 1
            self.set_auto_attach_interval(1)
            self.restart_rhsmcertd()
            if self.check_auto_attach_interval() == '1.0':
                logger.info("It's successful to enable healing feature")
            else:
                raise FailException("Test Failed - Failed to enable healing feature")
            # Restore the default auto-attach interval as 1440
            self.set_auto_attach_interval(1440)
            self.restart_rhsmcertd()
            if self.check_auto_attach_interval() == '1440.0':
                logger.info("It's successful to restore auto-attach interval")
            else:
                raise FailException("Test Failed - Failed to  restore auto-attach interval")
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
