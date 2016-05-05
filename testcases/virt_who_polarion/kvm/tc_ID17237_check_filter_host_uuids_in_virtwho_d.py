from utils import *
from testcases.virt_who_polarion.kvmbase import KVMBase
from utils.exception.failexception import FailException

class tc_ID17237_check_filter_host_uuids_in_virtwho_d(KVMBase):
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

#             (1) Filter_host_uuid=host_uuid, check virt-who send correct host/guest mapping to server
            self.set_filter_host_uuids("libvirt", host_uuid, remote_ip_2)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, targetmachine_ip=remote_ip_2)
            # (2) Filter_host_uuid="", check host/guest mapping 
            self.set_filter_host_uuids("libvirt", "\"\"", remote_ip_2)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False, targetmachine_ip=remote_ip_2)
            # (3) Filter_host_uuid='', check host/guest mapping 
            self.set_filter_host_uuids("libvirt", "\'\'", remote_ip_2)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False, targetmachine_ip=remote_ip_2)
            # (4) Filter_host_uuid=, check host/guest mapping 
            self.set_filter_host_uuids("libvirt", "", remote_ip_2)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False, targetmachine_ip=remote_ip_2)
            # (5) Filter_host_uuid="host_uuid","host_uuid_sec", virt-who will filter out host_uuid, it will not filter host_uuid_sec
            self.set_filter_host_uuids("libvirt", "\"%s\",\"%s\"" % (host_uuid, host_uuid_sec), remote_ip_2)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, targetmachine_ip=remote_ip_2)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_sec, "", uuid_exist=False, targetmachine_ip=remote_ip_2)
            # (6) Filter_host_uuid='host_uuid','host_uuid_sec', virt-who will filter out host_uuid, it will not filter host_uuid_sec
            self.set_filter_host_uuids("libvirt", "\'%s\',\'%s\'" % (host_uuid, host_uuid_sec), remote_ip_2)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, targetmachine_ip=remote_ip_2)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_sec, "", uuid_exist=False, targetmachine_ip=remote_ip_2)
            # (7) Filter_host_uuid='host_uuid', 'host_uuid_sec', virt-who will filter out host_uuid, it will not filter host_uuid_sec
            self.set_filter_host_uuids("libvirt", "\'%s\',  \'%s\'" % (host_uuid, host_uuid_sec), remote_ip_2)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, targetmachine_ip=remote_ip_2)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_sec, "", uuid_exist=False, targetmachine_ip=remote_ip_2)

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
