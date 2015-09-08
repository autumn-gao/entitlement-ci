"""******************************************

@author        : shihliu@redhat.com
@date        : 2013-03-11

******************************************"""

from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID183419_list_consumed_pool(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = RHSMConstants().get_constant("username")
            password = RHSMConstants().get_constant("password")
            self.sub_register(username, password)
            autosubprod = RHSMConstants().get_constant("autosubprod")
            self.sub_autosubscribe(autosubprod)
            #list consumed subscriptions
            installedproductname = RHSMConstants().get_constant("installedproductname")
            self.list_consumed_subscriptions(installedproductname)
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def list_consumed_subscriptions(self, installedproductname):
        cmd="subscription-manager list --consumed"
        (ret,output)=self.runcmd(cmd,"list consumed subscriptions")
        output_join = " ".join(x.strip() for x in output.split())
        if ret == 0 and ((installedproductname in output) or (installedproductname in output_join)):
            logger.info("It's successful to list all consumed subscriptions.")
            return True
        else:
            raise FailException("Test Failed - Failed to list all consumed subscriptions.")

if __name__ == "__main__":
    unittest.main()
