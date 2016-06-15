from utils import *
from testcases.virt_who_polarion.xenbase import XENBase
from utils.exception.failexception import FailException

class tc_ID17202_XEN_check_oneshot_function_by_cli(XENBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.runcmd_service("stop_virtwho")
            # (1) Check h/g mapping info show only once when run "virt-who --xen -o -d"
            # also check virt-who threads will not increase after run "-o -d" many times
            cmd = self.virtwho_cli("xen") + " -o -d"
            for i in range(1, 5):
                self.vw_check_mapping_info_number(cmd, 1)
            self.check_virtwho_thread(0)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.runcmd_service("restart_virtwho")
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
