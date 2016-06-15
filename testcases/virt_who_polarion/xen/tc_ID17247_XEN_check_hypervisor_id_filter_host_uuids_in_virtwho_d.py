from utils import *
from testcases.virt_who_polarion.xenbase import XENBase
from utils.exception.failexception import FailException

class tc_ID17247_XEN_check_hypervisor_id_filter_host_uuids_in_virtwho_d(XENBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.runcmd_service("stop_virtwho")
            self.config_option_disable("VIRTWHO_XEN")

            guest_name = self.get_vw_guest_name("XEN_GUEST_NAME")
            hyperv_host_ip = self.get_vw_cons("XEN_HOST")
            guest_uuid = self.hyperv_get_guest_guid(guest_name)
            host_uuid = self.hyperv_get_host_uuid()
            hyperv_host_name = self.hyperv_get_hostname(hyperv_host_ip)

            # (1) Set hypervisor_id=uuid, and fitler_host_uuids, it will show host/guest uuid mapping info
            self.set_hypervisor_id_filter_host_uuids("hyperv", "uuid", host_uuid)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            self.vw_check_message_in_rhsm_log(hyperv_host_name, message_exists=False)
            # (2) Set hypervisor_id=hostname, and fitler_host_uuids, it will show host/guest name mapping info
            self.set_hypervisor_id_filter_host_uuids("hyperv", "hostname", hyperv_host_name)
            self.vw_check_mapping_info_in_rhsm_log(hyperv_host_name, guest_uuid)
            self.vw_check_message_in_rhsm_log(host_uuid, message_exists=False)

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
