from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509835_pool_id_should_exist_in_list_consumed(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # register
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)

            # attach a pool
            pools=self.sub_list_availablepool_list()
            cmd = 'subscription-manager attach --pool=%s'%pools[0]
            (ret, output) = self.runcmd(cmd, "attach pools")
            if ret ==0 and "Successfully attached a subscription for" in output:
                logger.info("It's successful to attach a pool.")
            else:
                raise FailException("Test Failed - failed to attach a pool")

            # Check pool in 'list consumed'
            cmd = 'subscription-manager list --consumed | grep "Pool ID"'
            (ret, output) = self.runcmd(cmd, "list repos")
            if ret ==0 and pools[0] in output:
                logger.info("It's successful to check pool id in listing consumed")
            else:
                raise FailException("Test Failed - failed to check pool id in listing consumed")
        except Exception, e:
            logger.error(str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("=========== End of Running Test Case: %s ===========" % case_name)

if __name__ == "__main__":
    unittest.main()
