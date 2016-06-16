from utils import *
from testcases.virt_who_polarion.xenbase import XENBase
from utils.exception.failexception import FailException

class tc_ID17224_XEN_check_mapping_after_restart_virtwho_and_rhsm(XENBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            xen_host_ip = self.get_vw_cons("XEN_HOST")
            guest_name = self.get_vw_guest_name("XEN_GUEST_NAME")
            guestuuid = self.xen_get_guest_uuid(guest_name, xen_host_ip)
            hostuuid = self.xen_get_host_uuid(xen_host_ip)

            # (1) Check host/guest mapping info is exist 
            self.hypervisor_check_uuid(hostuuid, guestuuid, uuidexists=False)
            # (2) Check host/guest mapping has not update after restart rhsmcert
            self.xen_start_guest(guest_name, xen_host_ip)
            self.vw_check_message_in_rhsm_log("ERROR", message_exists=False, checkcmd="service rhsmcertd restart")
            # (3) Check host/guest mapping info is exist after restart virt-who 
            self.hypervisor_check_uuid(hostuuid, guestuuid)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.xen_stop_guest(guest_name, xen_host_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
