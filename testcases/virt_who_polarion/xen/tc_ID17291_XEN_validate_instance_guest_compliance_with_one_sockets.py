from utils import *
from testcases.virt_who_polarion.xenbase import XENBase
from utils.exception.failexception import FailException

class tc_ID17291_XEN_validate_instance_guest_compliance_with_one_sockets(XENBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            guest_name = self.get_vw_guest_name("XEN_GUEST_NAME")
            test_sku = self.get_vw_cons("instancebase_sku_id")
            sku_name = self.get_vw_cons("instancebase_name")

            self.hyperv_start_guest(guest_name)
            guestip = self.hyperv_get_guest_ip(guest_name)

            # register guest to SAM
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)

            # Set up guest socket to 1
            self.setup_custom_facts("cpu.cpu_socket(s)", "1")
            poolid = self.get_pool_by_SKU(test_sku, guestip)

            # (1) Subscribe guest to unspecify instance pool
            # check the instance pool Available on guest before subscribed
            instance_quantity_before = self.get_SKU_attribute(test_sku, "Available", guestip)
            self.sub_subscribetopool(poolid, guestip)
            # check consumed subscriptions' quality, should be 1 on guest 
            consumed_quantity_key = "QuantityUsed"
            consumed_quantity_value = "1"
            self.check_consumed_status(test_sku, consumed_quantity_key, consumed_quantity_value, guestip)
            # check consumed subscription with Status Details: 'Subscription is current'
            self.check_consumed_status(test_sku, "StatusDetails", "Subscription is current", guestip)
            # check the Status of installed product, should be 'Subscribed' status
            installed_status_key = "Status"
            installed_status_value = "Subscribed"
            self.check_installed_status(installed_status_key, installed_status_value, guestip)
            # check the instance pool Available on guest after subscribed
            instance_quantity_after = self.get_SKU_attribute(test_sku, "Available", guestip)
            # check the result, before - after = 1
            if int(instance_quantity_before) - int(instance_quantity_after) == 1:
                logger.info("Succeeded to check, the instance quantity is right.")
            else:
                raise FailException("Failed to check, the instance quantity is not right.")
            # (2) Subscribe guest to 1 instance pool
            self.sub_unsubscribe(guestip)
            self.sub_limited_subscribetopool(poolid, "1", guestip)
            # check consumed subscriptions' quality, should be 1 on guest 
            consumed_quantity_key = "QuantityUsed"
            consumed_quantity_value = "1"
            self.check_consumed_status(test_sku, consumed_quantity_key, consumed_quantity_value, guestip)
            # check consumed subscription with Status Details: 'Subscription is current'
            self.check_consumed_status(test_sku, "StatusDetails", "Subscription is current", guestip)
            # check the Status of installed product, should be 'Subscribed' status
            installed_status_key = "Status"
            installed_status_value = "Subscribed"
            self.check_installed_status(installed_status_key, installed_status_value, guestip)
            # (3) Subscribe guest to 2 instance pool
            self.sub_unsubscribe(guestip)
            self.sub_limited_subscribetopool(poolid, "2", guestip)
            # check consumed subscription with Status Details: 'Subscription is current'
            self.check_consumed_status(test_sku, "StatusDetails", "Subscription is current", guestip)
            # check the Status of installed product, should be 'Subscribed' status
            installed_status_key = "Status"
            installed_status_value = "Subscribed"
            self.check_installed_status(installed_status_key, installed_status_value, guestip)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            self.hyperv_stop_guest(guest_name)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
