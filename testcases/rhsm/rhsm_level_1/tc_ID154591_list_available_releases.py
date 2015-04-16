from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID154591_list_available_releases(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        # register to server
        username = RHSMConstants().get_constant("username")
        password = RHSMConstants().get_constant("password")
        self.sub_register(username, password)

        try:
            # auto subscribe to a pool
            autosubprod = RHSMConstants().get_constant("autosubprod")
            self.sub_autosubscribe(autosubprod)
            # list available releases
            currentversion = self.sub_getcurrentversion()
            cmd = "subscription-manager release --list"
            (ret, output) = self.runcmd(cmd, "list available releases")
            if ret == 0 and currentversion in output:
                logger.info("It's successful to list available releases.")
            else:
                raise FailException("Test Failed - Failed to list available releases.")
            self.assert_(True, case_name)
        except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
