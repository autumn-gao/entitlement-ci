from utils import *
from testcases.virt_who_polarion.kvmbase import KVMBase
from utils.exception.failexception import FailException

class tc_ID17241_check_filter_exclude_host_uuids_in_virtwho_d(KVMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.runcmd_service("stop_virtwho")
            remote_ip_2 = get_exported_param("REMOTE_IP_2")
            guest_name = self.get_vw_cons("KVM_GUEST_NAME")
            self.vw_define_guest(guest_name)
            guest_uuid = self.vw_get_uuid(guest_name)
            host_uuid = self.get_host_uuid()
            host_uuid_sec = "test"

            # (1) Set filter_host_uuid=host_uuid and exclude_host_uuid=host_uuid_sec, it will show host_uuid not host_uuid_sec
            self.set_filter_exclude_host_uuids("libvirt", host_uuid, host_uuid_sec, remote_ip_2)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, targetmachine_ip=remote_ip_2)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_sec, uuid_exist=False, targetmachine_ip=remote_ip_2)
            # (2) Set filter_host_uuid=host_uuid_sec and exclude_host_uuid=host_uuid_sec, it will not show host_uuid and host_uuid_sec
            self.set_filter_exclude_host_uuids("libvirt", host_uuid_sec, host_uuid, remote_ip_2)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False, targetmachine_ip=remote_ip_2)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_sec, uuid_exist=False, targetmachine_ip=remote_ip_2)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.unset_all_virtwho_d_conf(remote_ip_2)
            self.runcmd_service("restart_virtwho", remote_ip_2)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
