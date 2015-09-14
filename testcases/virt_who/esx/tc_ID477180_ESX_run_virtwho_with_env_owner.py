from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID477180_ESX_run_virtwho_with_env_owner(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            esx_owner = VIRTWHOConstants().get_constant("VIRTWHO_ESX_OWNER")
            esx_env = VIRTWHOConstants().get_constant("VIRTWHO_ESX_ENV")
            esx_server = VIRTWHOConstants().get_constant("VIRTWHO_ESX_SERVER")
            esx_username = VIRTWHOConstants().get_constant("VIRTWHO_ESX_USERNAME")
            esx_password = VIRTWHOConstants().get_constant("VIRTWHO_ESX_PASSWORD")

            guest_name = VIRTWHOConstants().get_constant("ESX_GUEST_NAME")
            destination_ip = VIRTWHOConstants().get_constant("ESX_HOST")
            host_uuid = self.esx_get_host_uuid(destination_ip)

            #0).check the guest is power off or not on esxi host, if power on, stop it firstly 
            if self.esx_guest_ispoweron(guest_name, destination_ip):
                self.esx_stop_guest(guest_name, destination_ip)
            self.esx_start_guest(guest_name)
            guestip = self.esx_get_guest_ip(guest_name, destination_ip)
            guestuuid = self.esx_get_guest_uuid(guest_name, destination_ip)
 
            #1). restart virt-who service for register esxi hypervisor
            self.service_command("restart_virtwho")

            #2). stop virt-who service
            self.service_command("stop_virtwho")

            #3). run virt-who with an wrong --esx-owner=xxxxxx
            cmd = "virt-who --esx --esx-owner=xxxxxx --esx-env=%s --esx-server=%s --esx-username=%s --esx-password=%s -o -d" %(esx_env,esx_server,esx_username,esx_password)
            ret, output = self.runcmd(cmd, "executing virt-who with an wrong: --esx-owner=xxxxxx")
            if ret == 0 and "ERROR" in output:
                logger.info("Succeeded to check, with an wrong esx-owner, no host/guest mapping send.")
            elif host_uuid in output and guestuuid in output:
                raise FailException("Failed to check, with an wrong esx-owner, virt-who should not send host/guest mapping.")
            else:
                raise FailException("Failed to run virt-who with an wrong esx-owner.")

            #4). run virt-who with an wrong ----esx-env=xxxxxx
            cmd = "virt-who --esx --esx-owner=%s --esx-env=xxxxxx --esx-server=%s --esx-username=%s --esx-password=%s -o -d" %(esx_owner,esx_server,esx_username,esx_password)
            ret, output = self.runcmd(cmd, "executing virt-who with an wrong: --esx-env=xxxxxx")
            if ret == 0 and "ERROR" in output:
                logger.info("Succeeded to check, with an wrong esx-env, no host/guest mapping send.")
            elif host_uuid in output and guestuuid in output:
                raise FailException("Failed to check, with an wrong esx-env, virt-who should not send host/guest mapping.")
            else:
                raise FailException("Failed to run virt-who with an wrong esx-env.")

            #5). run virt-who with an wrong ----esx-env=xxxxxx and --esx-owner=xxxxxx
            cmd = "virt-who --esx --esx-owner=xxxxxx --esx-env=xxxxxx --esx-server=%s --esx-username=%s --esx-password=%s -o -d" %(esx_server,esx_username,esx_password)
            ret, output = self.runcmd(cmd, "executing virt-who with an wrong: --esx-env=xxxxxx and --esx-owner=xxxxxx")
            if ret == 0 and "ERROR" in output:
                logger.info("Succeeded to check, with an wrong esx-env and esx-owner, no host/guest mapping send.")
            elif host_uuid in output and guestuuid in output:
                raise FailException("Failed to check, with an wrong esx-env and esx-owner, virt-who should not send host/guest mapping.")
            else:
                raise FailException("Failed to run virt-who with an wrong esx-env and esx-owner.")

            #6). run virt-who with right --esx-owner=%s --esx-env=%s
            cmd = "virt-who --esx --esx-owner=%s --esx-env=%s --esx-server=%s --esx-username=%s --esx-password=%s -o -d" %(esx_owner,esx_env,esx_server,esx_username,esx_password)
            ret, output = self.runcmd(cmd, "executing virt-who with an right: --esx-env and --esx-owner")
            if ret == 0 and host_uuid in output and guestuuid in output:
                logger.info("Succeeded to check, with an right esx-env and esx-owner, host/guest mapping can be sent.")
            else:
                raise FailException("Failed to run virt-who with an right esx-env and esx-owner.")

            #7). update vrit-who config with an wrong esx_owner, esx_env 
            self.update_esx_vw_configure("xxxxxx", "xxxxxx", esx_server, esx_username, esx_password)

            #7.1). after stop virt-who, start to monitor the rhsm.log 
            self.service_command("stop_virtwho")
            rhsmlogfile = "/var/log/rhsm/rhsm.log"
            cmd = "tail -f -n 0 %s > /tmp/tail.rhsm.log 2>&1 &" % rhsmlogfile
            self.runcmd(cmd, "generate nohup.out file by tail -f")

            #7.2). virt-who restart
            self.service_command("restart_virtwho")
            virtwho_status = self.check_virtwho_status()
            if virtwho_status == "running" or virtwho_status == "active":
                logger.info("Succeeded to check, virt-who is running whit an wrong esx_owner, esx_env.")
            else:
                raise FailException("Failed to check, virt-who is not running or active with an wrong esx_owner, esx_env.")

            #7.3). after restart virt-who, stop to monitor the rhsm.log
            time.sleep(5)
            cmd = "killall -9 tail ; cat /tmp/tail.rhsm.log"
            ret, output = self.runcmd(cmd, "feedback tail log for parse")
            if ret == 0 and output is not None and "ERROR" in output:
                logger.info("Succeeded to check, can find the Error info in rhsm.log with an wrong env and owner.")
            else:
                raise FailException("Failed to check, no Error info found in rhsm.log with an wrong env and owner")

            #8). update vrit-who config with an right esx_owner, esx_env 
            self.update_esx_vw_configure(esx_owner, esx_env, esx_server, esx_username, esx_password)

            #8.1). after stop virt-who, start to monitor the rhsm.log 
            self.service_command("stop_virtwho")
            rhsmlogfile = "/var/log/rhsm/rhsm.log"
            cmd = "tail -f -n 0 %s > /tmp/tail.rhsm.log 2>&1 &" % rhsmlogfile
            self.runcmd(cmd, "generate nohup.out file by tail -f")

            #8.2). virt-who restart
            self.service_command("restart_virtwho")
            virtwho_status = self.check_virtwho_status()
            if virtwho_status == "running" or virtwho_status == "active":
                logger.info("Succeeded to check, virt-who is running whit an wrong esx_owner, esx_env.")
            else:
                raise FailException("Failed to check, virt-who is not running or active with an wrong esx_owner, esx_env.")

            #8.3). after restart virt-who, stop to monitor the rhsm.log
            time.sleep(5)
            cmd = "killall -9 tail ; cat /tmp/tail.rhsm.log"
            ret, output = self.runcmd(cmd, "feedback tail log for parse")
            if ret == 0 and output is not None and "ERROR" not in output:
                rex = re.compile(r'Sending update in hosts-to-guests mapping: {.*?\d{4}-\d{1,2}-\d{1,2}', re.S)
                if len(rex.findall(output))>0:
                    mapping_info = rex.findall(output)[0]
                    if host_uuid in mapping_info and guestuuid in mapping_info:
                        logger.info("Succeeded to check uuid list, can find host/guest association info from rhsm.log.")
            else:
                raise FailException("Failed to check uuid list, no host/guest association info found from rhsm.log.")

            self.assert_(True, case_name)

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            self.esx_stop_guest(guest_name, destination_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
