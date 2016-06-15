from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509851_the_insecure_value_should_be_1_after_registering_with_insecure_option(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # Make sure the insecure value is 0 before registration
            self.set_insecure_value('0')

            # Register with --insecure option
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            cmd = "subscription-manager register --username=%s --password=%s --insecure"%(username, password)
            (ret, output) = self.runcmd(cmd, "register with --insecure option")
            if ret == 0 and "The system has been registered with ID:" in output:
                logger.info("It's successful to register with --insecure option")
            else:
                raise FailException("Test Failed - failed to register with --insecure option")

            # check insecure value after register with --insecure
            if self.check_insecure_value() == '1':
                logger.info("It's successful to check the insecure value is 1 after registering with --insecure option")
            else:
                raise FailException("Test Failed - failed to check the insecure value is 1 after registering with --insecure option")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.set_insecure_value('0')
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
