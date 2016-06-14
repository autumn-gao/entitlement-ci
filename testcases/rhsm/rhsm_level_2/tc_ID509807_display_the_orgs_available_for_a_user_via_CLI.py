from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509807_display_the_orgs_available_for_a_user_via_CLI(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            # display multi orgs
            cmd = 'subscription-manager orgs --username=%s --password=%s | grep Name | wc -l'%(username,password)
            (ret, output) = self.runcmd(cmd, "list multiple orgs")
            if ret ==0 and int(output)>=1:
                logger.info("It's successful to list multiple orgs")
            else:
                raise FailException("Test Failed - failed to list multiple orgs")
        except Exception, e:
            logger.error(str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("=========== End of Running Test Case: %s ===========" % case_name)

if __name__ == "__main__":
    unittest.main()
