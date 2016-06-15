from utils import *
from testcases.virt_who_polarion.xenbase import XENBase
from utils.exception.failexception import FailException

class tc_ID17290_XEN_validate_instance_host_with_multi_sockets_autosubscribe(XENBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            test_sku = self.get_vw_cons("instancebase_sku_id")
            sku_name = self.get_vw_cons("instancebase_name")

            # Set up guest facts
            self.setup_custom_facts("cpu.cpu_socket(s)", "8")
            poolid = self.get_pool_by_SKU(test_sku)

            # (1) Subscribe host to unspecify instance pool
            self.sub_subscribetopool(poolid)
            # check consumed subscriptions' quality, should be 1 on guest 
            consumed_quantity_key = "QuantityUsed"
            consumed_quantity_value = "8"
            self.check_consumed_status(test_sku, consumed_quantity_key, consumed_quantity_value)
            # check consumed subscription with Status Details: 'Subscription is current'
            self.check_consumed_status(test_sku, "StatusDetails", "Subscription is current")
            # check the Status of installed product, should be 'Subscribed' status
            installed_status_key = "Status"
            installed_status_value = "Subscribed"
            self.check_installed_status(installed_status_key, installed_status_value)

            # (2) Subscribe host to 1 instance pool
            self.sub_unsubscribe()
            cmd = "subscription-manager subscribe --pool=%s --quantity=1" % poolid
            ret, output = self.runcmd(cmd, "Check subscribe instance with non-multiple of the instance-multiplier")
            if ret != 0 and (("is not a multiple ") or ("quantity evenly divisible by 2") in output): 
                logger.info("Succeeded to check subscribe instance with non-multiple of the instance-multiplier.")
            else:
                raise FailException("Failed to check subscribe instance with non-multiple of the instance-multiplier.")

            # (3) Subscribe the registered host to 2 instance pool
            self.sub_unsubscribe()
            self.sub_limited_subscribetopool(poolid, "2")
            # check consumed subscriptions' quality, should be 2 on host 
            self.check_consumed_status(test_sku, "QuantityUsed", "2")
            # .check the Status of installed product, should be 'Partially Subscribed' status
            self.check_installed_status("Status", "Partially Subscribed")
            self.check_installed_status("StatusDetails", "Only supports 2 of 8 sockets.")

            # (4) Auto subscribe host
            self.sub_auto_subscribe()
            # check the Status of installed product, should be 'Subscribed' status
            self.check_installed_status("Status", "Subscribed")
            self.check_installed_status("StatusDetails", "")

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            # resume host facts
            self.restore_facts()
            # unsubscribe host
            self.sub_unsubscribe()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
