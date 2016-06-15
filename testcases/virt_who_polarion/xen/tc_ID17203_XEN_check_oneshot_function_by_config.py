from utils import *
from testcases.virt_who_polarion.xenbase import XENBase
from utils.exception.failexception import FailException

class tc_ID17203_XEN_check_oneshot_function_by_config(XENBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.runcmd_service("stop_virtwho")
            # (1) Enable VIRTWHO_ONE_SHOT, check h/g mapping info show only once
            self.config_option_disable("VIRTWHO_INTERVAL")
            self.config_option_setup_value("VIRTWHO_ONE_SHOT", 1)
            tmp_file = "/tmp/tail.rhsm.log"
            checkcmd = self.get_service_cmd("restart_virtwho")
            self.generate_tmp_log(checkcmd, tmp_file)
            cmd = "cat %s" % tmp_file
            self.vw_check_mapping_info_number(cmd, 1)
            self.check_virtwho_thread(0)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.config_option_disable("VIRTWHO_ONE_SHOT")
            self.runcmd_service("restart_virtwho")
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
