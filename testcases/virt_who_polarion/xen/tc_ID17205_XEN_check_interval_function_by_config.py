from utils import *
from testcases.virt_who_polarion.xenbase import XENBase
from utils.exception.failexception import FailException

class tc_ID17205_XEN_check_interval_function_by_config(XENBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.runcmd_service("stop_virtwho")
            self.config_option_disable("VIRTWHO_INTERVAL")
            check_msg = "hasn't changed, not sending"
            # (1) Check virt-who refresh default interval is 60s
            self.vw_check_message_number_in_rhsm_log(check_msg, 2, 150)
            # (2) Check virt-who refresh interval is 60 when config interval less than 60s
            self.runcmd_service("stop_virtwho")
            self.config_option_setup_value("VIRTWHO_INTERVAL", 10)
            self.vw_check_message_number_in_rhsm_log(check_msg, 2, 150)
            # (3) Check virt-who refresh interval is equal to config interval when config interval over 60s
            self.runcmd_service("stop_virtwho")
            self.check_virtwho_thread(0)
            self.config_option_setup_value("VIRTWHO_INTERVAL", 120)
            self.vw_check_message_number_in_rhsm_log(check_msg, 1, 150)
            #(4).Check virt-who thread will not increase after restart it.
            for i in range(5):
                self.runcmd_service("restart_virtwho")
                self.check_virtwho_thread(2)
                time.sleep(5)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.config_option_disable("VIRTWHO_INTERVAL")
            self.runcmd_service("restart_virtwho")
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
