from utils import *
from testcases.virt_who_polarion.xenbase import XENBase
from utils.exception.failexception import FailException

class tc_ID17219_XEN_check_vw_config_permission(XENBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            virt_who_conf_file = "/etc/sysconfig/virt-who"
            virt_who_pid_file = "/var/run/virt-who.pid"
            self.cm_check_file_mode(virt_who_conf_file, "600")
            self.runcmd_service("restart_virtwho")
            self.cm_check_file_mode(virt_who_pid_file, "600")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
