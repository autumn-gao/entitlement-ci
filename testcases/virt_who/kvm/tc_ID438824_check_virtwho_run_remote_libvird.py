from utils import *
from testcases.virt_who.kvmbase import KVMBase
from utils.exception.failexception import FailException
import paramiko

class tc_ID438824_check_virtwho_run_remote_libvird(KVMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            remote_ip_2 = get_exported_param("REMOTE_IP_2")
            remote_ip = get_exported_param("REMOTE_IP")
            username = "root"
            password = "red2015"
            guest_name = self.get_vw_cons("KVM_GUEST_NAME")
            guestuuid = self.vw_get_uuid(guest_name)

            # stop virt-who service on host1
            self.vw_stop_virtwho_new()
            # configure remote libvirt mode on host2
            self.set_remote_libvirt_conf(remote_ip, remote_ip_2)
            # undefine a guest    
            self.vw_undefine_guest(guest_name)
            # check if the uuid is correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=False, targetmachine_ip=remote_ip_2)
            # define a guest
            self.vw_define_guest(guest_name)
            guestuuid = self.vw_get_uuid(guest_name)
            # check if the uuid is correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=True, targetmachine_ip=remote_ip_2)

            self.assert_(True, case_name)

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.vw_define_all_guests()
            self.clean_remote_libvirt_conf(remote_ip_2)
            self.vw_restart_virtwho_new()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
