from utils import *
from testcases.virt_who_polarion.xenbase import XENBase
from utils.exception.failexception import FailException

class tc_ID17238_XEN_check_exclude_host_uuids_in_virtwho_d(XENBase):
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

            # (1) Exclude_host_uuid=host_uuid, check host_uuid will not send.
            self.set_exclude_host_uuids("xen", host_uuid)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False)
            # (2) Exclude_host_uuid=host_uuid_sec, check host_uuid will send. host_uuid will not send out
            self.set_exclude_host_uuids("xen", host_uuid_sec)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_sec, "", uuid_exist=False)
            # (3) Exclude_host_uuid="",check host/guest mapping will send out.
            self.set_exclude_host_uuids("xen", "\"\"")
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            # (4) Exclude_host_uuid='',check host/guest mapping will send out.
            self.set_exclude_host_uuids("xen", "\'\'")
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            # (5) Exclude_host_uuid=, check host/guest mapping will send out.
            self.set_exclude_host_uuids("xen", "")
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid)
            # (6) Exclude_host_uuid="host_uuid","host_uuid_sec", virt-who will not send host_uuid, host_uuid_sec
            self.set_exclude_host_uuids("xen", "\"%s\",\"%s\"" % (host_uuid, host_uuid_sec))
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_sec, "", uuid_exist=False)
            # (7) Exclude_host_uuid='host_uuid','host_uuid_sec', virt-who will not send host_uuid, host_uuid_sec
            self.set_exclude_host_uuids("xen", "\'%s\',\'%s\'" % (host_uuid, host_uuid_sec))
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False)
            self.vw_check_mapping_info_in_rhsm_log(host_uuid_sec, "", uuid_exist=False)
            # (8) Exclude_host_uuid='host_uuid', 'host_uuid_sec',virt-who will not send host_uuid, host_uuid_sec
            self.set_exclude_host_uuids("xen", "\'%s\',  \'%s\'" % (host_uuid, host_uuid_sec))
            self.vw_check_mapping_info_in_rhsm_log(host_uuid, guest_uuid, uuid_exist=False)
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
