from utils import *
from testcases.virt_who_polarion.xenbase import XENBase
from utils.exception.failexception import FailException

class tc_ID17216_XEN_check_env_option_by_cli(XENBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            error_msg_without_env = self.get_vw_cons("xen_error_msg_without_env")
            error_msg_with_wrong_env = self.get_vw_cons("xen_error_msg_with_wrong_env")
            xen_owner, xen_env, xen_server, xen_username, xen_password = self.get_xen_info()
            self.runcmd_service("stop_virtwho")

            # (1) When "--xen-env" is not exist, virt-who should show error info
            cmd_without_owner = "virt-who --xen --xen-owner=%s --xen-server=%s --xen-username=%s --xen-password=%s" % (xen_owner, xen_server, xen_username, xen_password) + " -o -d"
            self.vw_check_message(cmd_without_owner, error_msg_without_env, cmd_retcode=1)
            # (2) When "--xen-env" with wrong config, virt-who should show error info
            cmd_with_wrong_owner = "virt-who --xen --xen-owner=%s --xen-env=%s --xen-server=%s --xen-username=%s --xen-password=%s" % (xen_owner, self.get_vw_cons("wrong_env"), xen_server, xen_username, xen_password) + " -o -d"
            self.vw_check_message(cmd_with_wrong_owner, error_msg_with_wrong_env)
            # (3) When "--xen-env" with correct config, virt-who should show error info
            cmd = "virt-who --xen --xen-owner=%s --xen-env=%s --xen-server=%s --xen-username=%s --xen-password=%s" % (xen_owner, xen_env, xen_server, xen_username, xen_password) + " -o -d"
            self.vw_check_mapping_info_number(cmd, 1)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
