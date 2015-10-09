from utils import *
from testcases.virt_who.kvmbase import KVMBase
from utils.exception.failexception import FailException

class tc_ID338068_check_execute_virtwho_o_overtime(KVMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            guest_name = self.get_vw_cons("KVM_GUEST_NAME")
            guestuuid = self.vw_get_uuid(guest_name)
            self.vw_stop_virtwho()

            # run cmd virt-who with -o and -d option in the host five times
            for i in range(1,5):
                cmd = "virt-who -o -d"
                ret, output = self.runcmd(cmd, "run virt-who -o -d command")
                if ret == 0 and ("Sending domain info" in output or "Sending list of uuids" in output) and "ERROR" not in output:
                    logger.info("Succeeded to execute virt-who with one-shot mode.")
                    # check if the uuid is correctly monitored by virt-who.
                    if guestuuid in output:
                        logger.info("Successed to check guest uuid when virt-who at one-shot mode")
                    else:
                        raise FailException("Failed to check guest uuid when virt-who at one-shot mode")
                else:
                    raise FailException("Failed to run virt-who -o -d.")
                logger.info("Run virt-who at one-shot mode at the %s time" %i)
                i = i + 1

            self.assert_(True, case_name)

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            # stop virt-who command line mode
            self.vw_restart_virtwho()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
