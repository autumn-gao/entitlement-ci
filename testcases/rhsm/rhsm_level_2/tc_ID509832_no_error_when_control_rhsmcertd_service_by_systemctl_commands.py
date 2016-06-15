from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509832_no_error_when_control_rhsmcertd_service_by_systemctl_commands(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # Check if the make sure the rhsmcertd.service exists and is enabled.
            cmd = 'rpm -ql subscription-manager | grep systemd'
            (ret, output) = self.runcmd(cmd, "check rhsmcertd.service exists")
            if ret ==0 and '/usr/lib/systemd/system/rhsmcertd.service' in output:
                logger.info("It's successful to check rhsmcertd.service exists")
            else:
                raise FailException("Test Failed - failed to check rhsmcertd.service exists")

            cmd = 'systemctl list-unit-files | grep rhsmcertd'
            (ret, output) = self.runcmd(cmd, "check rhsmcertd.service is enabled")
            if ret ==0 and 'rhsmcertd.service                           enabled' in output:
                logger.info("It's successful to check rhsmcertd.service is enabled")
            else:
                raise FailException("Test Failed - failed to check rhsmcertd.service is enabled")

            # Check if systemd rhsmcertd.service is enabled, active and running by systemctl commands
            cmd = 'systemctl is-enabled rhsmcertd.service'
            (ret, output) = self.runcmd(cmd, "check rhsmcertd.service is enabled by systemctl")
            if ret ==0 and 'enabled' in output:
                logger.info("It's successful to check rhsmcertd.service is enabled by systemctl")
            else:
                raise FailException("Test Failed - failed to check rhsmcertd.service is enabled by systemctl")

            cmd = 'systemctl is-active rhsmcertd.service'
            (ret, output) = self.runcmd(cmd, "check rhsmcertd.service is active by systemctl")
            if ret ==0 and 'active' in output:
                logger.info("It's successful to check rhsmcertd.service is active by systemctl")
            else:
                raise FailException("Test Failed - failed to check rhsmcertd.service is active by systemctl")

            cmd = 'systemctl status rhsmcertd.service'
            (ret, output) = self.runcmd(cmd, "check rhsmcertd.service is running by systemctl")
            if ret ==0 and 'Active: active (running) since' in output:
                logger.info("It's successful to check rhsmcertd.service is running by systemctl")
            else:
                raise FailException("Test Failed - failed to check rhsmcertd.service is running by systemctl")

            # Remove rhsmcertd.log content and restart rhsmcertd service
            cmd = 'echo "" > /var/log/rhsm/rhsmcertd'
            (ret, output) = self.runcmd(cmd, "Remove rhsmcertd.log content")
            if ret ==0:
                logger.info("It's successful to Remove rhsmcertd.log content")
            else:
                raise FailException("Test Failed - failed to Remove rhsmcertd.log content")

            self.restart_rhsmcertd()

            # Check hard-coded 2 minute delay before attempting to communicate with the candlepin server upon starting the rhsmcertd service is demonstrated.
            cmd = 'grep Waiting /var/log/rhsm/rhsmcertd.log'
            (ret, output) = self.runcmd(cmd, "check 2 mins delay")
            if ret ==0 and 'Waiting 120 second(s) [2.0 minute(s)] before running updates.' in output:
                logger.info("It's successful to check the hard-coded 2 minute delay before attempting to communicate with the candlepin server upon starting the rhsmcertd service is demonstrated following in the rhsmcertd.log")
            else:
                raise FailException("Test Failed - failed to check the hard-coded 2 minute delay before attempting to communicate with the candlepin server upon starting the rhsmcertd service is demonstrated following in the rhsmcertd.log")
        except Exception, e:
            logger.error(str(e))
            self.assert_(False, case_name)
        finally:
            self.restore_environment()
            logger.info("=========== End of Running Test Case: %s ===========" % case_name)

if __name__ == "__main__":
    unittest.main()
