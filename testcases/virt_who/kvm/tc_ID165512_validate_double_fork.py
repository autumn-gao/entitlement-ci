from utils import *
from testcases.virt_who.kvmbase import KVMBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID165512_validate_double_fork(KVMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SERVER_IP = get_exported_param("SERVER_IP")
            SERVER_HOSTNAME = get_exported_param("SERVER_HOSTNAME")
            SERVER_USER = VIRTWHOConstants().get_constant("SERVER_USER")
            SERVER_PASS = VIRTWHOConstants().get_constant("SERVER_PASS")

            guest_name = VIRTWHOConstants().get_constant("KVM_GUEST_NAME")
            guestuuid = self.vw_get_uuid(guest_name)

            slave_machine_ip = get_exported_param("REMOTE_IP_2")

            # (1) check guest uuid is exist.
            self.vw_restart_virtwho()
            self.vw_check_uuid(guestuuid, uuidexists=True)
            # (2) Check guest uuid is exist after restart virt-who on another host
            self.vw_restart_virtwho(slave_machine_ip)
            self.vw_check_uuid(guestuuid, uuidexists=True)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.vw_define_guest(guest_name)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
