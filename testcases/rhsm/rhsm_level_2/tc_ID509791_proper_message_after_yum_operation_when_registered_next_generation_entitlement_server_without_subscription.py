from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509791_proper_message_after_yum_operation_when_registered_next_generation_entitlement_server_without_subscription(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            # yum operation
            cmd = 'yum repolist'
            (ret, output) = self.runcmd(cmd, "list repos")
            if ret ==0 and 'This system is registered to Red Hat Subscription Management, but is not receiving updates. You can use subscription-manager to assign subscriptions.' in output and 'repolist: 0' in output:
                logger.info("It's successful to show proper message after yum operation when registered without subscription to next generation entitlement server")
            else:
                raise FailException("Test Failed - failed to show proper message after yum operation when registered without subscription to next generation entitlement server")
        except Exception, e:
            logger.error(str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("=========== End of Running Test Case: %s ===========" % case_name)

if __name__ == "__main__":
    unittest.main()
