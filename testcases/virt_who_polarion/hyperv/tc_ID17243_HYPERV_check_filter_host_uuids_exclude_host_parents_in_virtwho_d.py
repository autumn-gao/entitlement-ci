from utils import *
from testcases.virt_who_polarion.hypervbase import HYPERVBase
from utils.exception.failexception import FailException

class tc_ID17243_HYPERV_check_filter_host_uuids_exclude_host_parents_in_virtwho_d(HYPERVBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.runcmd_service("stop_virtwho")
            self.config_option_disable("VIRTWHO_HYPERV")

            guest_name = self.get_vw_cons("HYPERV_GUEST_NAME")
            hyperv_host_ip = self.get_vw_cons("HYPERV_HOST")
            guest_uuid = self.hyperv_get_guest_guid(guest_name)
            host_uuid = self.hyperv_get_host_uuid()

            #(1) Set Filter_host_uuid and exclude_host_parents, it will show error info,it will filter host/guest mapping info
            self.set_filter_host_uuids_exclude_parents("hyperv", host_uuid, "host_parents_exclude")
            chkmsg = "exclude_host_parents is not supported in hyperv mode, ignoring it"
            self.vw_check_message_in_rhsm_log(chkmsg, message_exists=True)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.unset_all_virtwho_d_conf()
            self.set_hyperv_conf()
            self.runcmd_service("restart_virtwho")
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
