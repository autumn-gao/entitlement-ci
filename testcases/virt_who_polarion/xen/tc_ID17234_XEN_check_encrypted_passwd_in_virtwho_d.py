from utils import *
from testcases.virt_who_polarion.xenbase import XENBase
from utils.exception.failexception import FailException

class tc_ID17234_XEN_check_encrypted_passwd_in_virtwho_d(XENBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            hyperv_owner, hyperv_env, hyperv_server, hyperv_username, hyperv_password = self.get_hyperv_info()
            self.runcmd_service("stop_virtwho")

            # (1) Disable hyperv mode in /etc/sysconfig/virt-who
            self.config_option_disable("VIRTWHO_XEN")
            # (2) Config correct encryped password of hyperv mode in /etc/virt-who.d/virtwho, check virt-who send h/g mapping successfully
            encrypted_password = self.run_virt_who_password(hyperv_password)
            self.set_encrypted_password("hyperv", encrypted_password)
            self.vw_check_mapping_info_number_in_rhsm_log()
            # (3) Config wrong encryped password of hyperv mode in /etc/virt-who.d/virtwho, check virt-who can't send h/g mapping 
            self.set_encrypted_password("hyperv", "xxxxxxxxxxxxxxxxxxx")
            self.vw_check_message_in_rhsm_log("Password can't be decrypted, possibly corrupted")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.unset_all_virtwho_d_conf()
            self.set_hyperv_conf()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
