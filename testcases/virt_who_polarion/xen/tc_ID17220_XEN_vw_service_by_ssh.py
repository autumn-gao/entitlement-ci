from utils import *
from testcases.virt_who_polarion.xenbase import XENBase
from utils.exception.failexception import FailException

class tc_ID17220_XEN_vw_service_by_ssh(XENBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            # (1) When remote restart virt-who service, it should success
            ssh_cmd = "ssh %s " % get_exported_param("REMOTE_IP") + self.get_service_cmd("restart_virtwho")
            ret, output = self.runcmd_local_pexpect(ssh_cmd, "red2015")
            if "Starting virt-who: [  OK  ]" in output:
                logger.info("Succeeded to run virt-who restart by ssh")
            else:
                raise FailException("Failed to run virt-who restart by ssh")

            # (2) When remote check virt-who status, it should success
            ssh_cmd = "ssh %s " % get_exported_param("REMOTE_IP") + self.get_service_cmd("status_virtwho")
            ret, output = self.runcmd_local_pexpect(ssh_cmd, "red2015")
            if "is running" in output:
                logger.info("Succeeded to run virt-who status by ssh")
            else:
                raise FailException("Failed to run virt-who status by ssh")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
