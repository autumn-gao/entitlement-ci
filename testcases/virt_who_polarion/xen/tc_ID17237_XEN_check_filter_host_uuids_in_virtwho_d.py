from utils import *
from testcases.virt_who_polarion.xenbase import XENBase
from utils.exception.failexception import FailException

class tc_ID17237_XEN_check_filter_host_uuids_in_virtwho_d(XENBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.runcmd_service("stop_virtwho")
            self.config_option_disable("VIRTWHO_XEN")

            guest_name = self.get_vw_guest_name("XEN_GUEST_NAME")
            xen_host_ip = self.get_vw_cons("XEN_HOST")
            guest_uuid = self.xen_get_guest_uuid(guest_name, xen_host_ip)
            host_uuid = self.xen_get_host_uuid(xen_host_ip)
            host_uuid_sec = "test"

            self.xen_start_guest(guest_name, xen_host_ip)

            # (1) Filter_host_uuid=host_uuid, check virt-who send correct host/guest mapping to server
            self.set_filter_host_uuids("xen", host_uuid)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            # (2) Filter_host_uuid="", check host/guest mapping 
            self.set_filter_host_uuids("xen", "\"\"")
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False)
            # (3) Filter_host_uuid='', check host/guest mapping 
            self.set_filter_host_uuids("xen", "\'\'")
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False)
            # (4) Filter_host_uuid=, check host/guest mapping 
            self.set_filter_host_uuids("xen", "")
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False)
            # (5) Filter_host_uuid="host_uuid","host_uuid_sec", virt-who will filter out host_uuid, it will not filter host_uuid_sec
            self.set_filter_host_uuids("xen", "\"%s\",\"%s\"" % (host_uuid, host_uuid_sec))
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_sec, "", uuid_exist=False)
            # (6) Filter_host_uuid='host_uuid','host_uuid_sec', virt-who will filter out host_uuid, it will not filter host_uuid_sec
            self.set_filter_host_uuids("xen", "\'%s\',\'%s\'" % (host_uuid, host_uuid_sec))
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_sec, "", uuid_exist=False)
            # (7) Filter_host_uuid='host_uuid', 'host_uuid_sec', virt-who will filter out host_uuid, it will not filter host_uuid_sec
            self.set_filter_host_uuids("xen", "\'%s\',  \'%s\'" % (host_uuid, host_uuid_sec))
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_sec, "", uuid_exist=False)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.unset_all_virtwho_d_conf()
            self.set_xen_conf()
            self.xen_stop_guest(guest_name, xen_host_ip)
            self.runcmd_service("restart_virtwho")
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
