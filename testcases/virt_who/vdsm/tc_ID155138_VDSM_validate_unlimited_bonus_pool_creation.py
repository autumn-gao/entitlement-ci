from utils import *
from testcases.virt_who.vdsmbase import VDSMBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID155138_VDSM_validate_unlimited_bonus_pool_creation(VDSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP = get_exported_param("SERVER_IP")
            SERVER_HOSTNAME = get_exported_param("SERVER_HOSTNAME")
            SERVER_USER = VIRTWHOConstants().get_constant("SERVER_USER")
            SERVER_PASS = VIRTWHOConstants().get_constant("SERVER_PASS")

            guest_name = VIRTWHOConstants().get_constant("RHEL_RHEVM_GUEST_NAME")
            rhevm_ip = VIRTWHOConstants().get_constant("RHEVM_HOST")

            test_sku = VIRTWHOConstants().get_constant("productid_unlimited_guest")
            bonus_quantity = VIRTWHOConstants().get_constant("guestlimit_unlimited_guest")
            sku_name = VIRTWHOConstants().get_constant("productname_unlimited_guest")

            self.rhevm_start_vm(guest_name, rhevm_ip)
            (guestip,host_id) = self.rhevm_get_guest_ip(guest_name, rhevm_ip)

            # register guest to SAM
            if not self.sub_isregistered(guestip):
                self.configure_testing_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)
            self.sub_subscribe_sku(test_sku)

            # list available pools of guest, check related bonus pool generated.
            new_available_poollist = self.sub_listavailpools(test_sku, guestip)
            if new_available_poollist != None:
                for item in range(0, len(new_available_poollist)):
                    if "Temporary" in new_available_poollist[item]["SubscriptionType"]:
                        raise FailException("virt-who failed to get host/guest mapping.")
                    if "Available" in new_available_poollist[item]:
                        SKU_Number = "Available"
                    else:
                        SKU_Number = "Quantity"
                    if new_available_poollist[item]["SKU"] == test_sku and self.check_type_virtual(new_available_poollist[item]) and new_available_poollist[item][SKU_Number] == bonus_quantity:
                        logger.info("Succeeded to list bonus pool of product %s" % sku_name) 
                self.assert_(True, case_name)
            else:
                raise FailException("Failed to get available pool list from guest.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            # unsubscribe host
            self.sub_unsubscribe()
            self.rhevm_stop_vm(guest_name, rhevm_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
