from utils import *
from testcases.virt_who_polarion.xenbase import XENBase
from utils.exception.failexception import FailException

class tc_ID17262_XEN_check_att_validate_compliance_after_pause_shutdown_vm(XENBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = self.get_vw_guest_name("XEN_GUEST_NAME")
            xen_host_ip = self.get_vw_cons("XEN_HOST")
            guest_uuid = self.xen_get_guest_uuid(guest_name, xen_host_ip)
            host_uuid = self.xen_get_host_uuid(xen_host_ip)
            self.xen_start_guest(guest_name, xen_host_ip)
            guestip = self.xen_get_guest_ip(guest_name, xen_host_ip)

            test_sku = self.get_vw_cons("datacenter_sku_id")
            guest_bonus_sku = self.get_vw_cons("datacenter_bonus_sku_id")
            sku_name = self.get_vw_cons("datacenter_name")

            # (1) Register guest to SAM and subscribe to the bonus pool
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)
            # subscribe the hypervsior1 to the physical pool which can generate bonus pool
            self.server_subscribe_system(host_uuid, self.get_poolid_by_SKU(test_sku), SERVER_IP)
            # subscribe the registered guest to the corresponding bonus pool
            self.sub_subscribe_to_bonus_pool(guest_bonus_sku, guestip)
            # list consumed subscriptions on guest
            self.sub_listconsumed(sku_name, guestip)
            # (2) Start guest , check guest's uuid and guest's attribute 
            self.hypervisor_check_uuid(host_uuid, guest_uuid, uuidexists=True)
            self.vw_check_attr(guest_name, 1, 'xen', 'xen', 1, guest_uuid)
            # (3) Pause guest    
            self.xen_suspend_guest(guest_name, xen_host_ip)
            # check if the uuid is correctly monitored by virt-who.
            self.hypervisor_check_uuid(host_uuid, guest_uuid, uuidexists=True)
            self.vw_check_attr(guest_name, 1, 'xen', 'xen', 3, guest_uuid)
            # (4) Resume guest    
            self.xen_resume_guest(guest_name, xen_host_ip)
            # check if the uuid is correctly monitored by virt-who on host1 and host2
            self.hypervisor_check_uuid(host_uuid, guest_uuid, uuidexists=True)
            self.vw_check_attr(guest_name, 1, 'xen', 'xen', 1, guest_uuid)
            # consumed subscriptions is still exist on guest
            self.sub_listconsumed(sku_name, guestip)
            # (5) Stop guest    
            self.xen_stop_guest(guest_name, xen_host_ip)
            # check if the uuid is correctly monitored by virt-who.
            self.hypervisor_check_uuid(host_uuid, guest_uuid, uuidexists=True)
            self.vw_check_attr(guest_name, 0, 'xen', 'xen', 5, guest_uuid)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.xen_start_guest(guest_name, xen_host_ip)
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            self.xen_stop_guest(guest_name, xen_host_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
