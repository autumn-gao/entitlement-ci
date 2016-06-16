from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509857_friendly_error_message_when_an_identity_cert_expires(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)

            # In order to not influent other test, just advance system time of client by 30 years
            self.set_system_time('20450101')

            # Check identity cert on client
            cmd = "subscription-manager identity"
            (ret, output) = self.runcmd(cmd, "Check identity cert")
            if ret !=0 and 'Your identity certificate has expired'in output:
                logger.info("It's successful to check identity cert")
            else:
                raise FailException("Test Failed - Failed to check identity cert")
            
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_system_time()
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
