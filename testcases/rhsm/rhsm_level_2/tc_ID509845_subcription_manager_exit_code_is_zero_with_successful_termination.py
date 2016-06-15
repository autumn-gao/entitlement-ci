from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509845_subcription_manager_exit_code_is_zero_with_successful_termination(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # Successful termination of subscription-manager
            cmd = "subscription-manager --help"
            (ret, output) = self.runcmd(cmd, "return code of successful sm")
            if ret ==0:
                logger.info("It's successful to check return code of successful sm.")
            else:
                raise FailException("Test Failed - failed to check return code of successful sm.")

            # Successful termination of rct
            cmd = "rct --help"
            (ret, output) = self.runcmd(cmd, "return code of successful rct")
            if ret ==0:
                logger.info("It's successful to check return code of successful rct.")
            else:
                raise FailException("Test Failed - failed to check return code of successful rct.")

        except Exception, e:
            logger.error(str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("=========== End of Running Test Case: %s ===========" % case_name)

if __name__ == "__main__":
    unittest.main()
