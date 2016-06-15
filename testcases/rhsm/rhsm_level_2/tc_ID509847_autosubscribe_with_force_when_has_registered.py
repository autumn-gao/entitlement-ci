from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509847_autosubscribe_with_force_when_has_registered(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # Register
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)

            # clean /var/log/rhsm/rhsm.log
            logfile='/var/log/rhsm/rhsm.log'
            self.clear_file_content(logfile)

            # autosubscribe with --force in CLI
            cmd = "subscription-manager register --username=%s --password=%s --force --autosubscribe"%(username, password)
            (ret, output) = self.runcmd(cmd, "autosubscribe with --force in CLI")
            if ret == 0 and ("The system has been registered with ID" in output or "The system has been registered with id" in output) and 'has been unregistered' in output and 'Status:       Subscribed' in output:
                logger.info("It's successful to autosubscribe with --force in CLI")
            else:
                raise FailException("Test Failed - failed to autosubscribe with --force in CLI")

            # check rhsm.log
            cmd = 'egrep "error|traceback" /var/log/rhsm/rhsm.log'
            (ret, output) = self.runcmd(cmd, "check rhsm.log")
            if ret == 1 and output == '':
                logger.info("It's successful to check rhsm.log")
            else:
                raise FailException("Test Failed - failed to check rhsm.log")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
