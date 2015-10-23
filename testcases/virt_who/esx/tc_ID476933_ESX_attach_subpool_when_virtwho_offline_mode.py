from utils import *
from testcases.virt_who.esxbase import ESXBase
from utils.exception.failexception import FailException

class tc_ID476933_ESX_attach_subpool_when_virtwho_offline_mode(ESXBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

            VIRTWHO_ESX_OWNER = self.get_vw_cons("VIRTWHO_ESX_OWNER")
            VIRTWHO_ESX_ENV = self.get_vw_cons("VIRTWHO_ESX_ENV")
            VIRTWHO_ESX_SERVER = self.get_vw_cons("VIRTWHO_ESX_SERVER")
            VIRTWHO_ESX_USERNAME = self.get_vw_cons("VIRTWHO_ESX_USERNAME")
            VIRTWHO_ESX_PASSWORD = self.get_vw_cons("VIRTWHO_ESX_PASSWORD")

            product_name = self.get_vw_cons("datacenter_name")
            host_sku_id = self.get_vw_cons("datacenter_sku_id")
            bonus_sku_id = self.get_vw_cons("datacenter_bonus_sku_id")
            bonus_quantity = self.get_vw_cons("datacenter_bonus_quantity")

            guest_name = self.get_vw_guest_name("ESX_GUEST_NAME")
            destination_ip = self.get_vw_cons("ESX_HOST")
            host_uuid = self.esx_get_host_uuid(destination_ip)

            #0).check the guest is power off or not on esxi host, if power on, stop it firstly 
            if self.esx_guest_ispoweron(guest_name, destination_ip):
                self.esx_stop_guest(guest_name, destination_ip)
            self.esx_start_guest(guest_name)
            guestip = self.esx_get_guest_ip(guest_name, destination_ip)
            guestuuid = self.esx_get_guest_uuid(guest_name, destination_ip)

            #1). stop virt-who firstly 
            self.service_command("stop_virtwho")

            #2). disable esx config
            self.unset_esx_conf()

            #3). create offline data
            offline_data = "/tmp/offline.dat"
            cmd = "virt-who --esx --esx-owner=%s --esx-env=%s --esx-server=%s --esx-username=%s --esx-password=%s -p -d > %s" %(VIRTWHO_ESX_OWNER,VIRTWHO_ESX_ENV,VIRTWHO_ESX_SERVER,VIRTWHO_ESX_USERNAME,VIRTWHO_ESX_PASSWORD,offline_data)
            ret, output = self.runcmd(cmd, "executing virt-who with -p -d for offline mode.")
            if ret == 0:
                logger.info("Succeeded to execute virt-who with -p -d for offline mode. ")
            else:
                raise FailException("Failed to execute virt-who with -o -d")

            #4). creat /etc/virt-who.d/virt.fake file for offline mode
            conf_file = "/etc/virt-who.d/virt.fake"
            conf_data = '''[fake-virt]
type=fake
file=%s
is_hypervisor=True
owner=%s
env=%s''' % (offline_data, VIRTWHO_ESX_OWNER, VIRTWHO_ESX_ENV)

            self.set_virtwho_d_conf(conf_file, conf_data)


            #5). after stop virt-who, start to monitor the rhsm.log 
            rhsmlogfile = "/var/log/rhsm/rhsm.log"
            cmd = "tail -f -n 0 %s > /tmp/tail.rhsm.log 2>&1 &" % rhsmlogfile
            self.runcmd(cmd, "generate nohup.out file by tail -f")

            #6). virt-who restart
            self.service_command("restart_virtwho")
            virtwho_status = self.check_virtwho_status()
            if virtwho_status == "running" or virtwho_status == "active":
                logger.info("Succeeded to check, virt-who is running when offline mode.")
            else:
                raise FailException("Failed to check, virt-who is not running or active when offline mode.")

            #7). after restart virt-who, stop to monitor the rhsm.log
            time.sleep(10)
            cmd = "killall -9 tail ; cat /tmp/tail.rhsm.log"
            ret, output = self.runcmd(cmd, "feedback tail log for parse")
            if "ERROR" not in output and host_uuid in output and guestuuid in output:
                logger.info("Succeeded to check, can find uuid and no error when offline mode.")
            else:
                raise FailException("Failed to check, can not find uuid and no error when offline mode.")

            #8).check DataCenter is exist on host/hpyervisor
            host_pool_id = self.get_poolid_by_SKU(host_sku_id)
            if host_pool_id is not None or host_pool_id !="":
                 logger.info("Succeeded to find the pool id of '%s': '%s'" % (host_sku_id, host_pool_id))
            else:
                raise FailException("Failed to find the pool id of %s" % host_sku_id)

            #9).register guest to SAM/Candlepin server with same username and password
            if not self.sub_isregistered(guestip):
                self.configure_server(SERVER_IP, SERVER_HOSTNAME, guestip)
                self.sub_register(SERVER_USER, SERVER_PASS, guestip)

            #10).subscribe successfully to the DataCenter subscription pool on host
            self.server_subscribe_system(host_uuid, host_pool_id, SERVER_IP)

            #11).check the bonus pool is available
            if self.check_bonus_isExist(bonus_sku_id, bonus_quantity, guestip) is True:
                logger.info("Succeeded to find the bonus pool of product '%s'" % product_name)
                self.assert_(True, case_name)
            else:
                raise FailException("Failed to find the bonus pool from guest.")

            #12).subscribe to the bonus pool. 
            self.sub_subscribe_sku(bonus_sku_id, guestip)

            #13).check the consumed product
            self.sub_listconsumed(product_name, guestip)

            self.assert_(True, case_name)

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.unset_virtwho_d_conf(conf_file)

            cmd = "rm -f %s" % offline_data
            self.runcmd(cmd, "run cmd: %s" % cmd)

            self.set_esx_conf()
            self.service_command("restart_virtwho")

            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            # Unregister the ESX host 
            self.server_unsubscribe_all_system(host_uuid, SERVER_IP)
            self.esx_stop_guest(guest_name, destination_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()

