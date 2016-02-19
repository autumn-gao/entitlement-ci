from utils import *
from testcases.virt_who_polarion.hypervbase import HYPERVBase
from utils.exception.failexception import FailException

class tc_ID17237_HYPERV_check_filter_host_uuids_in_virtwho_d(HYPERVBase):
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
            host_uuid_sec = "test"

            # (1) Filter_host_uuid=host_uuid, check virt-who send correct host/guest mapping to server
            self.set_filter_host_uuids("hyperv", host_uuid)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            # (2) Filter_host_uuid="", check host/guest mapping 
            self.set_filter_host_uuids("hyperv", "\"\"")
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False)
            # (3) Filter_host_uuid='', check host/guest mapping 
            self.set_filter_host_uuids("hyperv", "\'\'")
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False)
            # (4) Filter_host_uuid=, check host/guest mapping 
            self.set_filter_host_uuids("hyperv", "")
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False)
            # (5) Filter_host_uuid="host_uuid","host_uuid_sec", virt-who will filter out host_uuid, it will not filter host_uuid_sec
            self.set_filter_host_uuids("hyperv", "\"%s\",\"%s\"" % (host_uuid, host_uuid_sec))
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_sec, "", uuid_exist=False)
            # (6) Filter_host_uuid='host_uuid','host_uuid_sec', virt-who will filter out host_uuid, it will not filter host_uuid_sec
            self.set_filter_host_uuids("hyperv", "\'%s\',\'%s\'" % (host_uuid, host_uuid_sec))
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_sec, "", uuid_exist=False)
            # (7) Filter_host_uuid='host_uuid', 'host_uuid_sec', virt-who will filter out host_uuid, it will not filter host_uuid_sec
            self.set_filter_host_uuids("hyperv", "\'%s\',  \'%s\'" % (host_uuid, host_uuid_sec))
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_sec, "", uuid_exist=False)

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
