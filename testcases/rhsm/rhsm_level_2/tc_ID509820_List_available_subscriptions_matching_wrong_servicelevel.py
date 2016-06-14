from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509820_List_available_subscriptions_matching_wrong_servicelevel(RHSMBase):
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
            cmd = 'subscription-manager list --available --servicelevel=qianqian'
            (ret, output) = self.runcmd(cmd, "Check the system status")
            if ret ==0 and 'No available subscription pools were found matching the service level "qianqian".' in output:
                logger.info("It's successful to check SLA")
            else:
                raise FailException("Test Failed - failed to check SLA")

        except Exception, e:
            logger.error(str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("=========== End of Running Test Case: %s ===========" % case_name)

if __name__ == "__main__":
    unittest.main()
