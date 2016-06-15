"""
@author        : qianzhan@redhat.com
@date        : 2016-06-15
"""

from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509853_subscription_manager_yum_plugin_prints_warning_to_stderr(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # make sure unregister
            self.restore_environment()

            # yum operation
            cmd = "yum repolist"
            (ret, output) = self.runcmd(cmd, "yum operation")
            if ret == 0 and 'This system is not registered to Red Hat Subscription Management. You can use subscription-manager to register.' in output:
                logger.info("It's successful to check sm yum plugin prints warning")
            else:
                raise FailException("Test Failed - Failed to check sm yum plugin prints warning")

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
