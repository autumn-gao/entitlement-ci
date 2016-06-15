from utils import *
from testcases.virt_who_polarion.xenbase import XENBase
from utils.exception.failexception import FailException

class tc_ID17209_XEN_check_config_option_by_cli(XENBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.runcmd_service("stop_virtwho")
            self.config_option_disable("VIRTWHO_XEN")

#           (1) Check virt-who send h/g mapping info one time when run "virt-who -c "
            conf_file = "/etc/virt-who.d/virt-who"
            self.set_virtwho_sec_config("xen")
            cmd = "virt-who -c %s -o -d" % conf_file
            self.vw_check_mapping_info_number(cmd, 1)
#           (2) Check virt-who send h/g mapping info one time when run "virt-who -config "
            cmd = "virt-who --config=%s  -o -d" % conf_file
            self.vw_check_mapping_info_number(cmd, 1)

            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.unset_virtwho_d_conf(conf_file)
            self.set_hyperv_conf()
            self.runcmd_service("restart_virtwho")
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
