from utils import *
from testcases.virt_who_polarion.hypervbase import HYPERVBase
from utils.exception.failexception import FailException

class tc_ID17208_HYPERV_check_print_function_by_cli(HYPERVBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            self.runcmd_service("stop_virtwho")
#           (1) Check "DEBUG" info will not exist when run "virt-who --hyperv -p"
            self.config_option_setup_value("VIRTWHO_DEBUG", 0)
            # need to sleep for a second, or else virt-who pid hung up
            cmd = self.virtwho_cli("hyperv") + " -p | sleep 10"
            self.vw_check_message(cmd, "DEBUG", message_exists=False)
#           (2) Check "DEBUG" info is exist when run "virt-who --hyperv -p -d"
            cmd = self.virtwho_cli("hyperv") + " -p -d"
            self.vw_check_message(cmd, "DEBUG")
#           (3) Check jason info is exist in tmp_json.log
            tmp_json = "/tmp/tmp_json.log"
            cmd = self.virtwho_cli("hyperv") + " -p -d > %s" % tmp_json
            json_in_log = ordered(json.loads(self.vw_get_mapping_info(cmd)[0].strip()))
            cmd = "cat %s | python -mjson.tool" % tmp_json
            ret, output = self.runcmd(cmd, "parse json file generated by -p")
            json_printed = ordered(json.loads(output.strip()))
            if json_printed != json_in_log:
                logger.info("Test Failed - failed to check virt-who print json file compared with json in rhsm.log file")
                self.assert_(False, case_name)
            else:
                logger.info("Succeeded to check virt-who print json file compared with json in rhsm.log file")

                self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

def ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    else:
        return obj

if __name__ == "__main__":
    unittest.main()
