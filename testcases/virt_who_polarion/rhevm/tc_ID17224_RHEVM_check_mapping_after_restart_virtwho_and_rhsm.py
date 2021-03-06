from utils import *
from testcases.virt_who_polarion.vdsmbase import VDSMBase
from utils.exception.failexception import FailException

class tc_ID17224_RHEVM_check_mapping_after_restart_virtwho_and_rhsm(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            guest_name = self.get_vw_cons("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = get_exported_param("RHEVM_IP")
            guestuuid = self.vdsm_get_vm_uuid(guest_name, rhevm_ip)
            self.rhevm_start_vm(guest_name, rhevm_ip)
            (guestip, hostuuid) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)

            # (1) Check host/guest mapping info is exist 
            self.set_rhevm_conf()
            self.hypervisor_check_uuid(hostuuid, guestuuid)
#             self.vw_check_mapping_info_in_rhsm_log(hostuuid, guestuuid)
            # (2) Check host/guest mapping info is not exist after restart rhsmcert
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            self.vw_check_message_in_rhsm_log("ERROR", message_exists=False, checkcmd="service rhsmcertd restart")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
