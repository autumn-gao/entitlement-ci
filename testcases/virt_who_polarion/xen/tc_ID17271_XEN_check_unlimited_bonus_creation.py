from utils import *
from testcases.virt_who_polarion.xenbase import XENBase
from utils.exception.failexception import FailException

class tc_ID17271_XEN_check_unlimited_bonus_creation(XENBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            server_ip, server_hostname, server_user, server_pass = self.get_server_info()
            guest_name = self.get_vw_guest_name("XEN_GUEST_NAME")
            host_uuid = self.hyperv_get_host_uuid()

            sku_id = self.get_vw_cons("productid_unlimited_guest")
            sku_name = self.get_vw_cons("productname_unlimited_guest")
            sku_quantity = self.get_vw_cons("guestlimit_unlimited_guest")

            # (1) Start guest
            self.hyperv_start_guest(guest_name)
            guestip = self.hyperv_get_guest_ip(guest_name)
            # (2) Register guest to server
            if not self.sub_isregistered(guestip):
                self.configure_server(server_ip, server_hostname, guestip)
                self.sub_register(server_user, server_pass, guestip)
            # (3) Subscribe hypervisor
            self.server_subscribe_system(host_uuid, self.get_poolid_by_SKU(sku_id), server_ip)
            # (4) List available pools of guest, check related bonus pool generated.
            self.check_bonus_exist(sku_id, sku_quantity, guestip)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            self.hyperv_stop_guest(guest_name)
            self.server_unsubscribe_all_system(host_uuid, server_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
