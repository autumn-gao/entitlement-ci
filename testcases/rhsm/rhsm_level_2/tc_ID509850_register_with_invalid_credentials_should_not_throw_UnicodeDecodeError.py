from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509850_register_with_invalid_credentials_should_not_throw_UnicodeDecodeError(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # Clean /var/log/rhsm/rhsm.log
            logfile='/var/log/rhsm/rhsm.log'
            self.clear_file_content(logfile)

            # Register with invalid credential
            cmd = "LANG=de_DE.UTF-8 subscription-manager register --username=foo --password=bar"
            (ret, output) = self.runcmd(cmd, "Register with invalid credential")
            if ret != 0 and "Invalid credentials" in output and "codec can't decode" not in output:
                logger.info("It's successful to Register with invalid credential")
            else:
                raise FailException("Test Failed - failed to Register with invalid credential")

            # check rhsm.log
            cmd = 'egrep "exception|Exception" /var/log/rhsm/rhsm.log'
            (ret, output) = self.runcmd(cmd, "check rhsm.log")
            if ret ==0 and 'RestlibException: Invalid credentials' in output:
                logger.info("It's successful to check rhsm.log credentials exception")
            else:
                raise FailException("Test Failed - failed to check rhsm.log credentials exception")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
