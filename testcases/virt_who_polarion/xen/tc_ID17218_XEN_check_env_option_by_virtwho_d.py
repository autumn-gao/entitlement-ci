from utils import *
from testcases.virt_who_polarion.xenbase import XENBase
from utils.exception.failexception import FailException

class tc_ID17218_XEN_check_env_option_by_virtwho_d(XENBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            error_msg_without_env = self.get_vw_cons("xen_error_msg_without_env_in_conf")
            error_msg_with_wrong_env = self.get_vw_cons("xen_error_msg_with_wrong_env")
            xen_owner, xen_env, xen_server, xen_username, xen_password = self.get_xen_info()
            self.runcmd_service("stop_virtwho")
            self.config_option_disable("VIRTWHO_XEN")

            # (1) When "env" is not exist, virt-who should show error info
            self.set_virtwho_sec_config_with_keyvalue("xen", "env", "")
            self.vw_check_message(self.get_service_cmd("restart_virtwho"), error_msg_without_env, cmd_retcode=1)
            # (2) When "env" with wrong config, virt-who should show error info
            self.set_virtwho_sec_config_with_keyvalue("xen", "env", self.get_vw_cons("wrong_env"))
            self.vw_check_message_in_rhsm_log(error_msg_with_wrong_env)
            # (3) When "env" with correct config, virt-who should show error info
            self.set_virtwho_sec_config("xen")
            self.vw_check_mapping_info_number_in_rhsm_log()

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.unset_virtwho_d_conf("/etc/virt-who.d/virt-who")
            self.set_xen_conf()
            self.runcmd_service("restart_virtwho")
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
