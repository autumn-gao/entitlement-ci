from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509819_autosubscribe_when_the_system_status_is_valid(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # register
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)

            # auto-attach
            autosubprod = self.get_rhsm_cons("autosubprod")
            self.sub_autosubscribe(autosubprod)

            # Check the system status
            cmd = 'subscription-manager status'
            (ret, output) = self.runcmd(cmd, "Check the system status")
            if ret ==0 and 'Overall Status: Current' in output:
                logger.info("It's successful to Check the system status")
            else:
                raise FailException("Test Failed - failed to Check the system status")

            # auto-attach again
            cmd = 'subscription-manager attach'
            (ret, output) = self.runcmd(cmd, "check second auto-attach")
            if ret ==0 and 'All installed products are covered by valid entitlements. No need to update subscriptions at this time.' in output:
                logger.info("It's successful to check second auto-attach")
            else:
                raise FailException("Test Failed - failed to check second auto-attach")

        except Exception, e:
            logger.error(str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("=========== End of Running Test Case: %s ===========" % case_name)

if __name__ == "__main__":
    unittest.main()
