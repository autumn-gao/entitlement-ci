from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509855_remind_message_after_disabling_manage_repos_in_rhsm_conf(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            autosubprod = self.get_rhsm_cons("autosubprod")
            self.sub_autosubscribe(autosubprod)

            # Enable "manage_repos" in the rhsm.conf and check the repos
            self.set_manage_repos_value('1')

            # Check manage_repos_value
            if self.check_manage_repos_value() == '1':
                cmd = "subscription-manager repos --list"
                (ret, output) = self.runcmd(cmd,'get repos list')
                if ret == 0 and 'Available Repositories in /etc/yum.repos.d/redhat.repo' in output:
                    logger.info("It's successful to get repos list")
                else:
                    raise FailException("Test Failed - Failed to get repos list")
            else:
                raise FailException("Test Failed - Failed to check manage_repos, the value is not 1")

            # Disable "manage_repos" in the rhsm.conf and check the repos
            self.set_manage_repos_value('0')

            # Check manage_repos_value
            if self.check_manage_repos_value() == '0':
                cmd = "subscription-manager repos --list"
                (ret, output) = self.runcmd(cmd,'get repos list')
                if ret == 0 and 'Repositories disabled by configuration.' in output:
                    logger.info("It's successful to check reminding message")
                else:
                    raise FailException("Test Failed - Failed to check reminding message")
            else:
                raise FailException("Test Failed - Failed to check manage_repos, the value is not 0")

            self.assert_(True, case_name)

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)

        finally:
            self.set_manage_repos_value('1')
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def check_manage_repos_value(self):
        cmd = "grep manage_repos /etc/rhsm/rhsm.conf"
        (ret, output) = self.runcmd(cmd,'get manage_repos value')
        if ret == 0:
            logger.info("It's successful to get manage_repos value")
            return output.split('=')[1].strip()
        else:
            raise FailException("Test Failed - Failed to check manage_repos")

    def set_manage_repos_value(self, value):
        cmd="sed -i '/manage_repos/d' /etc/rhsm/rhsm.conf;sed -i '/# Manage generation of yum repositories for subscribed content:/a\manage_repos = %s' /etc/rhsm/rhsm.conf"%value
        (ret, output) = self.runcmd(cmd,'set manage_repos value')
        if ret == 0 and self.check_manage_repos_value() == value:
            logger.info("It's successful to set manage_repos value")
        else:
            raise FailException("Test Failed - Failed to set manage_repos value")

if __name__ == "__main__":
    unittest.main()
