from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509792_proper_message_after_yum_operation_when_registered_next_generation_entitlement_server_with_expired_subscription(RHSMBase):
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

            # set client's system time as expired date(in order to not influence other test with server, not set server's system time as expired date)
            self.set_system_time(20200101)

            # yum operation
            cmd = 'yum repolist'
            (ret, output) = self.runcmd(cmd, "list repos")
            if ret ==0 and 'The subscription for following product(s) has expired:' in output and 'repolist: 0' in output:
                logger.info("It's successful to show proper message after yum operation when registered with expired subscription to next generation entitlement server")
            else:
                raise FailException("Test Failed - failed to show proper message after yum operation when registered with expired subscription to next generation entitlement server")
        except Exception, e:
            logger.error(str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_system_time()
            self.restore_environment()
            logger.info("=========== End of Running Test Case: %s ===========" % case_name)

if __name__ == "__main__":
    unittest.main()
