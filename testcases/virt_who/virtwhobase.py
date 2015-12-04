from utils import *
from testcases.base import Base
from utils.exception.failexception import FailException
from utils.libvirtAPI.Python.xmlbuilder import XmlBuilder

class VIRTWHOBase(Base):
    # ========================================================
    #       Basic Functions
    # ========================================================

    def brew_virtwho_upgrate(self, targetmachine_ip=None):
        # virt-who upgrade via brew
        brew_virt_who = get_exported_param("BREW_VIRTWHO")
        cmd = "yum -y upgrade %s" % brew_virt_who
        ret, output = self.runcmd(cmd, "upgrade virt-who via brew", targetmachine_ip)

    def upstream_virtwho_install(self, targetmachine_ip=None):
        # virt-who install via upstream
        github_url = get_exported_param("GITHUB_URL")
        cmd = "git clone %s; cd virt-who; make install" % github_url
        ret, output = self.runcmd(cmd, "install virt-who via upstream", targetmachine_ip)

    def sys_setup(self):
        # system setup for virt-who testing
        cmd = "yum install -y virt-who"
        ret, output = self.runcmd(cmd, "install virt-who for esx testing", showlogger=False)
        if ret == 0:
            logger.info("Succeeded to setup system for virt-who testing.")
        else:
            raise FailException("Test Failed - Failed to setup system for virt-who testing.")

    def install_desktop(self, targetmachine_ip=""):
        if self.os_serial == "7":
            cmd = "yum install -y @gnome-desktop tigervnc-server"
            ret, output = self.runcmd(cmd, "install desktop and tigervnc", targetmachine_ip, showlogger=False)
            if ret == 0:
                logger.info("Succeeded to install @gnome-desktop tigervnc-server")
            else:
                raise FailException("Test Failed - Failed to install @gnome-desktop tigervnc-server")
        else:
            cmd = "yum groupinstall -y 'X Window System' 'Desktop' 'Desktop Platform'"
            ret, output = self.runcmd(cmd, "install desktop", targetmachine_ip, showlogger=False)
            if ret == 0:
                logger.info("Succeeded to install 'X Window System' 'Desktop' 'Desktop Platform'")
            else:
                raise FailException("Test Failed - Failed to install 'X Window System' 'Desktop' 'Desktop Platform'")
            cmd = "yum install -y tigervnc-server"
            ret, output = self.runcmd(cmd, "install tigervnc", targetmachine_ip, showlogger=False)
            if ret == 0:
                logger.info("Succeeded to install tigervnc-server")
            else:
                raise FailException("Test Failed - Failed to install tigervnc-server")
        cmd = "ps -ef | grep Xvnc | grep -v grep"
        ret, output = self.runcmd(cmd, "check whether vpncserver has started", targetmachine_ip,)
        if ret == 0:
            logger.info("vncserver already started ...")
        else:
            cmd = "vncserver -SecurityTypes None"
            ret, output = self.runcmd(cmd, "start vncserver", targetmachine_ip)
            if ret == 0:
                logger.info("Succeeded to start vncserver")
            else:
                raise FailException("Test Failed - Failed to start vncserver")

    def stop_firewall(self, targetmachine_ip=""):
        ''' stop iptables service and setenforce as 0. '''
        # stop iptables service
        cmd = "service iptables stop"
        ret, output = self.runcmd(cmd, "Stop iptables service", targetmachine_ip)
        cmd = "service iptables status"
        ret, output = self.runcmd(cmd, "Chech iptables service status", targetmachine_ip)
        if ("Firewall is stopped" in output) or ("Firewall is not running" in output) or ("Active: inactive" in output):
            logger.info("Succeeded to stop iptables service.")
        else:
            logger.info("Failed to stop iptables service.")
        # setenforce as 0
        cmd = "setenforce 0"
        ret, output = self.runcmd(cmd, "Set setenforce 0", targetmachine_ip)
#         cmd = "sestatus"
#         ret, output = self.runcmd(cmd, "Check selinux status", targetmachine_ip)
#         if ret == 0 and "permissive" in output:
#             logger.info("Succeeded to setenforce as 0.")
#         else:
#             raise FailException("Failed to setenforce as 0.")
        # unfinished, close firewall and iptables for ever 

    def get_hostname(self, targetmachine_ip=""):
        cmd = "hostname"
        ret, output = self.runcmd(cmd, "geting the machine's hostname", targetmachine_ip)
        if ret == 0:
            hostname = output.strip(' \r\n').strip('\r\n') 
            logger.info("Succeeded to get the machine's hostname %s." % hostname) 
            return hostname
        else:
            raise FailException("Test Failed - Failed to get hostname in %s." % self.get_hg_info(targetmachine_ip))

    # only return CLI for virt-who esx mode, don't run cli 
    def virtwho_cli(self, mode):
        esx_owner = self.get_vw_cons("VIRTWHO_ESX_OWNER")
        esx_env = self.get_vw_cons("VIRTWHO_ESX_ENV")
        esx_server = self.get_vw_cons("VIRTWHO_ESX_SERVER")
        esx_username = self.get_vw_cons("VIRTWHO_ESX_USERNAME")
        esx_password = self.get_vw_cons("VIRTWHO_ESX_PASSWORD")

        if mode == "esx":
            cmd = "virt-who --esx --esx-owner=%s --esx-env=%s --esx-server=%s --esx-username=%s --esx-password=%s" % (esx_owner, esx_env, esx_server, esx_username, esx_password)
        else:
            raise FailException("Failed to execute virt-who with one shot")
        return cmd

    # run virt-who oneshot by cli, return the output
    def virtwho_oneshot(self, mode, targetmachine_ip=""):
        cmd = self.virtwho_cli(mode) + " -o -d "
        self.service_command("stop_virtwho")
        ret, output = self.runcmd(cmd, "executing virt-who with one shot")
        self.service_command("restart_virtwho")
        if ret == 0:
            logger.info("Succeeded to execute virt-who with one shot ")
            return ret, output
        else:
            raise FailException("Failed to execute virt-who with one shot")
    
    # check uuid from oneshot output 
    def check_uuid_oneshot(self, uuid, mode, targetmachine_ip=""):
        ret, output = self.virtwho_oneshot(mode, targetmachine_ip)
        if uuid in output:
            return True
        else:
            return False 

    # check systemd service is exist or not
    def check_systemctl_service(self, keyword, targetmachine_ip=""):
        cmd = "systemctl list-units|grep %s -i" % keyword
        ret, output = self.runcmd(cmd, "check %s service by systemctl" % keyword, targetmachine_ip)
        if ret == 0:
            return True
        return False

    # check virt-who servcie status, rhel7:"active" "failed" "unknown", rhel6:"running" "stopped"
    def check_virtwho_status(self, targetmachine_ip=""):
        if self.check_systemctl_service("virt-who", targetmachine_ip):
            # will feedback "active" "failed" "unknow"
            cmd = "systemctl is-active virt-who"
            ret, output = self.runcmd(cmd, "check virt-who service by systemctl.", targetmachine_ip)
            return output.strip()
        else:
            # will feedback "running" "stopped" "failed"
            cmd = "service virt-who status"
            ret, output = self.runcmd(cmd, "check virt-who service status by sysvinit", targetmachine_ip)
            if "running" in output:
                return "running"
            elif "stopped" in output:
                return "stopped"
            else:
                return "failed"

    def vw_restart_virtwho(self, targetmachine_ip=""):
        ''' restart virt-who service. '''
        cmd = "service virt-who restart"
        ret, output = self.runcmd(cmd, "restart virt-who", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to restart virt-who service.")
        else:
            raise FailException("Test Failed - Failed to restart virt-who service.")

    def check_virtwho_thread(self, targetmachine_ip=""):
        ''' check virt-who thread number '''
        cmd = "ps -ef | grep -v grep | grep virt-who |wc -l"
        ret, output = self.runcmd(cmd, "check virt-who thread", targetmachine_ip)
        if ret == 0 and output.strip() == "2":
            logger.info("Succeeded to check virt-who thread number is 2.")
        else:
            raise FailException("Test Failed - Failed to check virt-who thread number is 2.")

    def config_virtwho_interval(self, interval_value, targetmachine_ip=""):
        # clean # for VIRTWHO_INTERVAL 
        cmd = "sed -i 's/^#VIRTWHO_INTERVAL/VIRTWHO_INTERVAL/' /etc/sysconfig/virt-who"
        (ret, output) = self.runcmd(cmd, "uncomment VIRTWHO_INTERVAL firstly in virt-who config file", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to uncomment VIRTWHO_INTERVAL.")
        else:
            raise FailException("Failed to uncomment VIRTWHO_INTERVAL.")

        # set VIRTWHO_INTERVAL value
        cmd = "sed -i 's/^VIRTWHO_INTERVAL=.*/VIRTWHO_INTERVAL=%s/' /etc/sysconfig/virt-who" % interval_value
        (ret, output) = self.runcmd(cmd, "set VIRTWHO_INTERVAL to %s" % interval_value, targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to set VIRTWHO_INTERVAL=%s" % interval_value)
        else:
            raise FailException("Failed to set VIRTWHO_INTERVAL=%s" % interval_value)

    def set_virtwho_d_conf(self, file_name, file_data, targetmachine_ip=""):
        cmd = '''cat > %s <<EOF
%s 
EOF''' % (file_name, file_data)
        ret, output = self.runcmd(cmd, "create config file: %s" % file_name, targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to create config file: %s" % file_name)
        else:
            raise FailException("Test Failed - Failed to create config file %s" % file_name)

    def unset_virtwho_d_conf(self, file_name, targetmachine_ip=""):
        cmd = "rm -f %s" % file_name
        ret, output = self.runcmd(cmd, "run cmd: %s" % cmd, targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to remove %s" % file_name)
        else:
            raise FailException("Test Failed - Failed to remove %s" % file_name)

    def run_virt_who_password(self, input_password, timeout=None):
        import paramiko
        remote_ip = get_exported_param("REMOTE_IP")
        username = "root"
        password = "red2015"
        virt_who_password_cmd = "python /usr/share/virt-who/virtwhopassword.py" 
        logger.info("run command %s in %s" % (virt_who_password_cmd, remote_ip))
        
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(remote_ip, 22, username, password)
        channel = ssh.get_transport().open_session()
        channel.settimeout(600)
        channel.get_pty()
        channel.exec_command(virt_who_password_cmd)
        output = ""
        while True:
            data = channel.recv(1048576)
            output += data
            if channel.send_ready():
                if data.strip().endswith('Password:'):
                    channel.send(input_password + '\n')
                if channel.exit_status_ready():
                    break
        if channel.recv_ready():
            data = channel.recv(1048576)
            output += data

        if channel.recv_exit_status() == 0 and output is not None:
            logger.info("Succeeded to encode password: %s" % input_password)
            encode_password = output.split('\n')[2].strip()
            return encode_password 
        else:
            raise FailException("Failed to encode virt-who-password.")

    def vw_stop_virtwho(self, targetmachine_ip=""):
        ''' stop virt-who service. '''
        cmd = "service virt-who stop"
        ret, output = self.runcmd(cmd, "stop virt-who", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to stop virt-who service.")
        else:
            raise FailException("Failed to stop virt-who service.")

    def vw_restart_libvirtd(self, targetmachine_ip=""):
        ''' restart libvirtd service. '''
        cmd = "service libvirtd restart"
        ret, output = self.runcmd(cmd, "restart libvirtd", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to restart libvirtd service.")
        else:
            raise FailException("Test Failed - Failed to restart libvirtd")

    def vw_restart_virtwho_new(self, targetmachine_ip=""):
        if self.check_systemctl_service("virt-who", targetmachine_ip):
            cmd = "systemctl restart virt-who.service; sleep 10"
            ret, output = self.runcmd(cmd, "restart virt-who service by systemctl.", targetmachine_ip)
            if ret == 0:
                logger.info("Succeeded to restsart virt-who")
            else:
                raise FailException("Test Failed - Failed to restart virt-who")
        else:
            cmd = "service virt-who restart; sleep 10"
            ret, output = self.runcmd(cmd, "restart virt-who by service", targetmachine_ip)
            if ret == 0:
                logger.info("Succeeded to restsart virt-who")
            else:
                raise FailException("Test Failed - Failed to restart virt-who")

    def vw_stop_virtwho_new(self, targetmachine_ip=""):
        if self.check_systemctl_service("virt-who", targetmachine_ip):
            cmd = "systemctl stop virt-who.service; sleep 10"
            ret, output = self.runcmd(cmd, "stop virt-who service by systemctl.", targetmachine_ip)
            if ret == 0:
                logger.info("Succeeded to stop virt-who")
            else:
                raise FailException("Test Failed - Failed to stop virt-who")
        else:
            cmd = "service virt-who stop; sleep 10"
            ret, output = self.runcmd(cmd, "stop virt-who by service", targetmachine_ip)
            if ret == 0:
                logger.info("Succeeded to stop virt-who")
            else:
                raise FailException("Test Failed - Failed to stop virt-who")

    def vw_check_virtwho_status(self, targetmachine_ip=""):
        ''' Check the virt-who status. '''
        if self.get_os_serials(targetmachine_ip) == "7":
            cmd = "systemctl status virt-who; sleep 10"
            ret, output = self.runcmd(cmd, "virt-who status", targetmachine_ip)
            if ret == 0 and "running" in output:
            # if ret == 0:
                logger.info("Succeeded to check virt-who is running.")
            else:
                raise FailException("Test Failed - Failed to check virt-who is running.")
        else:
            cmd = "service virt-who status; sleep 10"
            ret, output = self.runcmd(cmd, "virt-who status", targetmachine_ip)
            if ret == 0 and "running" in output:
                logger.info("Succeeded to check virt-who is running.")
            else:
                raise FailException("Test Failed - Failed to check virt-who is running.")

    def vw_check_libvirtd_status(self, targetmachine_ip=""):
        ''' Check the libvirtd status. '''
        if self.get_os_serials(targetmachine_ip) == "7":
            cmd = "systemctl status libvirtd; sleep 10"
            ret, output = self.runcmd(cmd, "virt-who status", targetmachine_ip)
            if ret == 0 and "running" in output:
                logger.info("Succeeded to check libvirtd is running.")
            else:
                raise FailException("Test Failed - Failed to check libvirtd is running.")
        else:
            cmd = "service libvirtd status; sleep 10"
            ret, output = self.runcmd(cmd, "libvirtd status", targetmachine_ip)
            if ret == 0 and "running" in output:
                logger.info("Succeeded to check libvirtd is running.")
                self.SET_RESULT(0)
            else:
                raise FailException("Test Failed - Failed to check libvirtd is running.")

    def sub_isregistered(self, targetmachine_ip=""):
        ''' check whether the machine is registered. '''
        cmd = "subscription-manager identity"
        ret, output = self.runcmd(cmd, "check whether the machine is registered", targetmachine_ip)
        if ret == 0:
            logger.info("System %s is registered." % self.get_hg_info(targetmachine_ip))
            return True
        else: 
            logger.info("System %s is not registered." % self.get_hg_info(targetmachine_ip))
            return False

    def sub_register(self, username, password, targetmachine_ip=""):
        ''' register the machine. '''
        cmd = "subscription-manager register --username=%s --password=%s" % (username, password)
        ret, output = self.runcmd(cmd, "register system", targetmachine_ip)
        if ret == 0 or "The system has been registered with id:" in output or "This system is already registered" in output:
            logger.info("Succeeded to register system %s" % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Failed to register system %s" % self.get_hg_info(targetmachine_ip))

    def sub_unregister(self, targetmachine_ip=""):
        ''' Unregister the machine. '''
        if self.sub_isregistered(targetmachine_ip):
            # need to sleep before destroy guest or else register error happens 
            cmd = "subscription-manager unregister"
            ret, output = self.runcmd(cmd, "unregister system", targetmachine_ip)
            if ret == 0 :
                logger.info("Succeeded to unregister %s." % self.get_hg_info(targetmachine_ip))
            else:
                raise FailException("Failed to unregister %s." % self.get_hg_info(targetmachine_ip))

            # need to clean local data after unregister
            cmd = "subscription-manager clean"
            ret, output = self.runcmd(cmd, "clean system", targetmachine_ip)
            if ret == 0 :
                logger.info("Succeeded to clean %s." % self.get_hg_info(targetmachine_ip))
            else:
                raise FailException("Failed to clean %s." % self.get_hg_info(targetmachine_ip))
        else:
            logger.info("The machine is not registered to server now, no need to do unregister.")

    def sub_listavailpools(self, productid, targetmachine_ip="", showlog=True):
        ''' list available pools.'''
        cmd = "subscription-manager list --available"
        ret, output = self.runcmd(cmd, "run 'subscription-manager list --available'", targetmachine_ip, showlogger=showlog)
        if ret == 0:
            if "No Available subscription pools to list" not in output:
                if productid in output:
                    logger.info("Succeeded to run 'subscription-manager list --available' %s." % self.get_hg_info(targetmachine_ip))
                    pool_list = self.__parse_avail_pools(output)
                    return pool_list
                else:
                    raise FailException("Failed to run 'subscription-manager list --available' %s - Not the right available pools are listed!" % self.get_hg_info(targetmachine_ip))
            else:
                raise FailException("Failed to run 'subscription-manager list --available' %s - There is no Available subscription pools to list!" % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Failed to run 'subscription-manager list --available' %s." % self.get_hg_info(targetmachine_ip))

    def __parse_avail_pools(self, output):
        datalines = output.splitlines()
        pool_list = []
        data_segs = []
        segs = []
        for line in datalines:
            if ("Product Name:" in line) or ("ProductName:" in line) or ("Subscription Name:" in line):
                segs.append(line)
            elif segs:
                # change this section for more than 1 lines without ":" exist
                if ":" in line:
                    segs.append(line)
                else:
                    segs[-1] = segs[-1] + " " + line.strip()
            if ("Machine Type:" in line) or ("MachineType:" in line) or ("System Type:" in line):
                data_segs.append(segs)
                segs = []
        # parse detail information for each pool
        for seg in data_segs:
            pool_dict = {}
            for item in seg:
                keyitem = item.split(":")[0].replace(" ", "")
                valueitem = item.split(":")[1].strip()
                pool_dict[keyitem] = valueitem
            pool_list.append(pool_dict)
        return pool_list

    # used to parse the output for "subscribe list --installed"
    def __parse_installed_lines(self, output):
        datalines = output.splitlines()
        pool_list = []
        data_segs = []
        segs = []
        for line in datalines:
            if ("Product Name:" in line) or ("ProductName:" in line) or ("Subscription Name:" in line):
                segs.append(line)
            elif segs:
                # change this section for more than 1 lines without ":" exist
                if ":" in line:
                    segs.append(line)
                else:
                    segs[-1] = segs[-1] + " " + line.strip()
            if ("Ends:" in line):
                data_segs.append(segs)
                segs = []
        # parse detail information for each pool
        for seg in data_segs:
            pool_dict = {}
            for item in seg:
                keyitem = item.split(":")[0].replace(" ", "")
                valueitem = item.split(":")[1].strip()
                pool_dict[keyitem] = valueitem
            pool_list.append(pool_dict)
        return pool_list

    def __parse_listavailable_output(self, output):
        datalines = output.splitlines()
        data_list = []
        # split output into segmentations for each pool
        data_segs = []
        segs = []
        tmpline = ""
        for line in datalines:
            if ("Product Name:" in line) or ("ProductName" in line) or ("Subscription Name" in line):
                tmpline = line
            elif line and ":" not in line:
                tmpline = tmpline + ' ' + line.strip()
            elif line and ":" in line:
                segs.append(tmpline)
                tmpline = line
            if ("Machine Type:" in line) or ("MachineType:" in line) or ("System Type:" in line) or ("SystemType:" in line):
                segs.append(tmpline)
                data_segs.append(segs)
                segs = []
        for seg in data_segs:
            data_dict = {}
            for item in seg:
                keyitem = item.split(":")[0].replace(' ', '')
                valueitem = item.split(":")[1].strip()
                data_dict[keyitem] = valueitem
            data_list.append(data_dict)
        return data_list

    def get_pool_by_SKU(self, SKU_id, guest_ip=""):
        ''' get_pool_by_SKU '''
        availpoollistguest = self.sub_listavailpools(SKU_id, guest_ip)
        if availpoollistguest != None:
            for index in range(0, len(availpoollistguest)):
                if("SKU" in availpoollistguest[index] and availpoollistguest[index]["SKU"] == SKU_id):
                    rindex = index
                    break
            if "PoolID" in availpoollistguest[index]:
                gpoolid = availpoollistguest[rindex]["PoolID"]
            else:
                gpoolid = availpoollistguest[rindex]["PoolId"]
            return gpoolid
        else:
            logger.error("Failed to subscribe the guest to the bonus pool of the product: %s - due to failed to list available pools." % SKU_id)
            self.SET_RESULT(1)

    def sub_subscribe_to_bonus_pool(self, productid, guest_ip=""):
        ''' subscribe the registered guest to the corresponding bonus pool of the product: productid. '''
        availpoollistguest = self.sub_listavailpools(productid, guest_ip)
        if availpoollistguest != None:
            rindex = -1
            for index in range(0, len(availpoollistguest)):
                if("SKU" in availpoollistguest[index] and availpoollistguest[index]["SKU"] == productid and self.check_type_virtual(availpoollistguest[index])):
                    rindex = index
                    break
                elif("ProductId" in availpoollistguest[index] and availpoollistguest[index]["ProductId"] == productid and self.check_type_virtual(availpoollistguest[index])):
                    rindex = index
                    break
            if rindex == -1:
                raise FailException("Failed to show find the bonus pool")
            if "PoolID" in availpoollistguest[index]:
                gpoolid = availpoollistguest[rindex]["PoolID"]
            else:
                gpoolid = availpoollistguest[rindex]["PoolId"]
            self.sub_subscribetopool(gpoolid, guest_ip)
        else:
            raise FailException("Failed to subscribe the guest to the bonus pool of the product: %s - due to failed to list available pools." % productid)

    def sub_subscribe_sku(self, sku, targetmachine_ip=""):
        ''' subscribe by sku. '''
        availpoollist = self.sub_listavailpools(sku, targetmachine_ip)
        if availpoollist != None:
            rindex = -1
            for index in range(0, len(availpoollist)):
                if("SKU" in availpoollist[index] and availpoollist[index]["SKU"] == sku):
                    rindex = index
                    break
                elif("ProductId" in availpoollist[index] and availpoollist[index]["ProductId"] == sku):
                    rindex = index
                    break
            if rindex == -1:
                raise FailException("Failed to show find the bonus pool")
            if "PoolID" in availpoollist[index]:
                poolid = availpoollist[rindex]["PoolID"]
            else:
                poolid = availpoollist[rindex]["PoolId"]
            self.sub_subscribetopool(poolid, targetmachine_ip)
        else:
            raise FailException("Failed to subscribe to the pool of the product: %s - due to failed to list available pools." % sku)

    def sub_subscribetopool(self, poolid, targetmachine_ip=""):
        ''' subscribe to a pool. '''
        cmd = "subscription-manager subscribe --pool=%s" % (poolid)
        ret, output = self.runcmd(cmd, "subscribe by --pool", targetmachine_ip)
        if ret == 0:
            if "Successfully " in output:
                logger.info("Succeeded to subscribe to a pool %s." % self.get_hg_info(targetmachine_ip))
            else:
                raise FailException("Failed to show correct information after subscribing %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Failed to subscribe to a pool %s." % self.get_hg_info(targetmachine_ip))

    def sub_limited_subscribetopool(self, poolid, quality, targetmachine_ip=""):
        ''' subscribe to a pool. '''
        cmd = "subscription-manager subscribe --pool=%s --quantity=%s" % (poolid, quality)
        ret, output = self.runcmd(cmd, "subscribe by --pool --quanitity", targetmachine_ip)
        if ret == 0:
            if "Successfully " in output:
                logger.info("Succeeded to subscribe to limited pool %s." % self.get_hg_info(targetmachine_ip))
            else:
                raise FailException("Failed to show correct information after subscribing %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Failed to subscribe to a pool %s." % self.get_hg_info(targetmachine_ip))

    def sub_disable_auto_subscribe(self, targetmachine_ip=""):
        ''' Disable subscribe subscribe  '''
        cmd = "subscription-manager auto-attach --disable"
        ret, output = self.runcmd(cmd, "Disable auto-attach", targetmachine_ip)
        if ret == 0 and "disabled" in output:
            logger.info("Succeeded to Disable auto-attach %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Failed to Disable auto-attach %s." % self.get_hg_info(targetmachine_ip))

    def sub_auto_subscribe(self, targetmachine_ip=""):
        ''' subscribe to a pool by auto '''
        cmd = "subscription-manager subscribe --auto"
        ret, output = self.runcmd(cmd, "subscribe by --auto", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to subscribe to a pool %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Failed to subscribe to a pool %s." % self.get_hg_info(targetmachine_ip))

    def sub_unsubscribe(self, targetmachine_ip=""):
        ''' unsubscribe from all entitlements. '''
        cmd = "subscription-manager unsubscribe --all"
        ret, output = self.runcmd(cmd, "unsubscribe all", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to unsubscribe all in %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Failed to unsubscribe all in %s." % self.get_hg_info(targetmachine_ip))

    def sub_listconsumed(self, productname, targetmachine_ip="", productexists=True):
        ''' list consumed entitlements. '''
        cmd = "subscription-manager list --consumed"
        ret, output = self.runcmd(cmd, "list consumed subscriptions", targetmachine_ip)
        if ret == 0:
            if productexists:
                if "No consumed subscription pools to list" not in output:
                    if productname in output:
                        logger.info("Succeeded to list the right consumed subscription %s." % self.get_hg_info(targetmachine_ip))
                    else:
                        raise FailException("Failed to list consumed subscription %s - Not the right consumed subscription is listed!" % self.get_hg_info(targetmachine_ip))
                else:
                    raise FailException("Failed to list consumed subscription %s - There is no consumed subscription to list!")
            else:
                if productname not in output:
                    logger.info("Succeeded to check entitlements %s - the product '%s' is not subscribed now." % (self.get_hg_info(targetmachine_ip), productname))
                else:
                    raise FailException("Failed to check entitlements %s - the product '%s' is still subscribed now." % (self.get_hg_info(targetmachine_ip), productname))
        else:
            raise FailException("Failed to list consumed subscriptions.")

    # check "subscription-manager list --consumed" key & value 
    def check_consumed_status(self, sku_id, key="", value="", value2="", targetmachine_ip=""):
        ''' check consumed entitlements status details '''
        cmd = "subscription-manager list --consumed"
        ret, output = self.runcmd(cmd, "list consumed subscriptions", targetmachine_ip)
        if ret == 0 and output is not None:
            consumed_lines = self.__parse_avail_pools(output)
            if consumed_lines != None:
                for line in range(0, len(consumed_lines)):
                    if key is not None and (value is not None or value2 is not None):
                        if consumed_lines[line]["SKU"] == sku_id and consumed_lines[line][key] == value :
                            logger.info("Succeeded to list the right consumed subscription, %s=%s %s." % (key, value, self.get_hg_info(targetmachine_ip)))
                            return
                        elif consumed_lines[line]["SKU"] == sku_id and consumed_lines[line][key] == value2:
                            logger.info("Succeeded to list the right consumed subscription, %s=%s %s." % (key, value2, self.get_hg_info(targetmachine_ip)))
                            return
                    else:
                        if consumed_lines[line]["SKU"] == sku_id:
                            logger.info("Succeeded to list the right consumed subscription %s" % self.get_hg_info(targetmachine_ip))
                            return
                # no proper consumed subscription found
                raise FailException("Failed to list the right consumed subscriptions, %s=%s %s." % (key, value, self.get_hg_info(targetmachine_ip)))
            else:
                raise FailException("List consumed subscription: none %s" % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Failed to list consumed subscriptions.")

    # check "subscription-manager list --installed" key & value 
    def check_installed_status(self, key, value, targetmachine_ip=""):
        ''' check the installed entitlements. '''
        cmd = "subscription-manager list --installed"
        ret, output = self.runcmd(cmd, "list installed subscriptions", targetmachine_ip)
        if ret == 0 and output is not None :
            installed_lines = self.__parse_installed_lines(output)
            if installed_lines != None:
                for line in range(0, len(installed_lines)):
                    if installed_lines[line][key] == value:
                        logger.info("Succeeded to check installed status: %s %s" % (value, self.get_hg_info(targetmachine_ip)))
                        return
                # no proper installed status found
                raise FailException("Failed to check installed status %s %s" % (value, self.get_hg_info(targetmachine_ip)))
            else:
                raise FailException("List installed info: none %s" % self.get_hg_info(targetmachine_ip))
        raise FailException("Failed to list installed info.")

    # check ^Certificate: or ^Content: in cert file
    def check_cert_file(self, keywords, targetmachine_ip=""):
        cmd = "rct cat-cert /etc/pki/entitlement/*[^-key].pem | grep -A5 \"%s\"" % keywords
        ret, output = self.runcmd(cmd, "Check %s exist in cert file in guest" % keywords, targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to check content sets exist %s" % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Failed to check content sets exist %s" % self.get_hg_info(targetmachine_ip))

    # check ^Repo ID by subscription-manager repos --list 
    def check_yum_repo(self, keywords, targetmachine_ip=""):
        cmd = "subscription-manager repos --list | grep -A4 \"^Repo ID\""
        ret, output = self.runcmd(cmd, "Check repositories available in guest", targetmachine_ip)
        if ret == 0 and "This system has no repositories available through subscriptions." not in output:
            logger.info("Succeeded to check repositories available %s" % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Failed to check repositories available %s" % self.get_hg_info(targetmachine_ip))

    # get sku attribute value 
    def get_SKU_attribute(self, sku_id, attribute_key, targetmachine_ip=""):
        poollist = self.sub_listavailpools(sku_id, targetmachine_ip)
        if poollist != None:
            for index in range(0, len(poollist)):
                if("SKU" in poollist[index] and poollist[index]["SKU"] == sku_id):
                    rindex = index
                    break
            if attribute_key in poollist[index]:
                attribute_value = poollist[rindex][attribute_key]
                return attribute_value
            raise FailException("Failed to check, the attribute_key is not exist.")
        else:
            raise FailException("Failed to list available subscriptions")
                
    def sub_refresh(self, targetmachine_ip=""):
        ''' sleep 20 seconds firstly due to guest restart, and then refresh all local data. '''
        cmd = "sleep 20; subscription-manager refresh"
        ret, output = self.runcmd(cmd, "subscription fresh", targetmachine_ip)
        if ret == 0 and "All local data refreshed" in output:
            logger.info("Succeeded to refresh all local data %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Failed to refresh all local data %s." % self.get_hg_info(targetmachine_ip))

    def check_type_virtual(self, pool_dict):
        if "MachineType" in pool_dict.keys():
            TypeName = "MachineType"
        elif "SystemType" in pool_dict.keys():
            TypeName = "SystemType"
        return pool_dict[TypeName] == "Virtual" or pool_dict[TypeName] == "virtual"

    def check_bonus_isExist(self, sku_id, bonus_quantity, targetmachine_ip=""):
        # check bonus pool is exist or not
        cmd = "subscription-manager list --available"
        ret, output = self.runcmd(cmd, "run 'subscription-manager list --available'", targetmachine_ip)
        if ret == 0:
            if "No Available subscription pools to list" not in output:
                pool_list = self.__parse_avail_pools(output)
                if pool_list != None:
                    for item in range(0, len(pool_list)):
                        if "Available" in pool_list[item]:
                            SKU_Number = "Available"
                        else:
                            SKU_Number = "Quantity"
                        if pool_list[item]["SKU"] == sku_id and self.check_type_virtual(pool_list[item]) and pool_list[item][SKU_Number] == bonus_quantity:
                            return True
                    return False
                else:
                    raise FailException("Failed to list available pool, the pool is None.")
            else:
                raise FailException("Failed to list available pool, No Available subscription pools to list.")
        else:
            raise FailException("Failed to run 'subscription-manager list --available'")

    def setup_custom_facts(self, facts_key, facts_value, targetmachine_ip=""):
        ''' setup_custom_facts '''
        cmd = "echo '{\"" + facts_key + "\":\"" + facts_value + "\"}' > /etc/rhsm/facts/custom.facts"
        ret, output = self.runcmd(cmd, "create custom.facts", targetmachine_ip)
        if ret == 0 :
            logger.info("Succeeded to create custom.facts %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Failed to create custom.facts %s." % self.get_hg_info(targetmachine_ip))

        cmd = "subscription-manager facts --update"
        ret, output = self.runcmd(cmd, "update subscription facts", targetmachine_ip)
        if ret == 0 and "Successfully updated the system facts" in output:
            logger.info("Succeeded to update subscription facts %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Failed to update subscription facts %s." % self.get_hg_info(targetmachine_ip))

    def restore_facts(self, targetmachine_ip=""):
        ''' setup_custom_facts '''
        cmd = "rm -f /etc/rhsm/facts/custom.facts"
        ret, output = self.runcmd(cmd, "remove custom.facts", targetmachine_ip)
        if ret == 0 :
            logger.info("Succeeded to remove custom.facts %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Failed to remove custom.facts %s." % self.get_hg_info(targetmachine_ip))

        cmd = "subscription-manager facts --update"
        ret, output = self.runcmd(cmd, "update subscription facts", targetmachine_ip)
        if ret == 0 and "Successfully updated the system facts" in output:
            logger.info("Succeeded to update subscription facts %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Failed to update subscription facts %s." % self.get_hg_info(targetmachine_ip))

    def vw_check_uuid(self, guestuuid, uuidexists=True, rhsmlogpath='/var/log/rhsm', targetmachine_ip=""):
        ''' check if the guest uuid is correctly monitored by virt-who. '''
        rhsmlogfile = os.path.join(rhsmlogpath, "rhsm.log")
        if self.get_os_serials(targetmachine_ip) == "7":
            cmd = "nohup tail -f -n 0 %s > /tmp/tail.rhsm.log 2>&1 &" % rhsmlogfile
            ret, output = self.runcmd(cmd, "generate nohup.out file by tail -f", targetmachine_ip)
            # ignore restart virt-who serivce since virt-who -b -d will stop
            self.vw_restart_virtwho_new(targetmachine_ip)
            time.sleep(10)
            cmd = "killall -9 tail ; cat /tmp/tail.rhsm.log"
            ret, output = self.runcmd(cmd, "get log number added to rhsm.log", targetmachine_ip)
        else: 
            self.vw_restart_virtwho_new(targetmachine_ip)
            cmd = "tail -3 %s " % rhsmlogfile
            ret, output = self.runcmd(cmd, "check output in rhsm.log", targetmachine_ip)
        if ret == 0:
            if "Sending list of uuids: " in output:
                log_uuid_list = output.split('Sending list of uuids: ')[1]
                logger.info("Succeeded to get guest uuid.list from rhsm.log.")
            elif "Sending update to updateConsumer: " in output:
                log_uuid_list = output.split('Sending list of uuids: ')[1]
                logger.info("Succeeded to get guest uuid.list from rhsm.log.")
            elif "Sending domain info" in output:
                log_uuid_list = output.split('Sending domain info: ')[1]
                logger.info("Succeeded to get guest uuid.list from rhsm.log.")
            elif "Sending update in hosts-to-guests mapping" in output:
                log_uuid_list = output.split('Sending update in hosts-to-guests mapping: ')[1]
                logger.info("Succeeded to get guest uuid.list from rhsm.log.")
            else:
                raise FailException("Failed to get uuid list from rhsm.log")
            if uuidexists:
                if guestuuid == "" and len(log_uuid_list) == 0:
                    logger.info("Succeeded to get none uuid list")
                else:
                    if guestuuid in log_uuid_list:
                        logger.info("Succeeded to check guestuuid %s in log_uuid_list" % guestuuid)
                    else:
                        raise FailException("Failed to check guestuuid %s in log_uuid_list" % guestuuid)
            else:
                if guestuuid not in log_uuid_list:
                    logger.info("Succeeded to check guestuuid %s not in log_uuid_list" % guestuuid)
                else:
                    raise FailException("Failed to check guestuuid %s not in log_uuid_list" % guestuuid)
        else:
            raise FailException("Failed to get rhsm.log")

    def vw_check_attr(self, guestname, guest_status, guest_type, guest_hypertype, guest_state, guestuuid, rhsmlogpath='/var/log/rhsm', targetmachine_ip=""):
        ''' check if the guest attributions is correctly monitored by virt-who. '''
        rhsmlogfile = os.path.join(rhsmlogpath, "rhsm.log")
        if self.get_os_serials(targetmachine_ip) == "7":
            cmd = "nohup tail -f -n 0 %s > /tmp/tail.rhsm.log 2>&1 &" % rhsmlogfile
            ret, output = self.runcmd(cmd, "generate nohup.out file by tail -f", targetmachine_ip)
            self.vw_restart_virtwho(targetmachine_ip)
            time.sleep(10)
            cmd = "killall -9 tail ; cat /tmp/tail.rhsm.log"
            ret, output = self.runcmd(cmd, "get log number added to rhsm.log", targetmachine_ip)
        else: 
            self.vw_restart_virtwho(targetmachine_ip)
            cmd = "tail -3 %s " % rhsmlogfile
            ret, output = self.runcmd(cmd, "check output in rhsm.log", targetmachine_ip)
        if ret == 0:
            ''' get guest uuid.list from rhsm.log '''
            if "Sending list of uuids: " in output:
                log_uuid_list = output.split('Sending list of uuids: ')[1]
                logger.info("Succeeded to get guest uuid.list from rhsm.log.")
            elif "Sending update to updateConsumer: " in output:
                log_uuid_list = output.split('Sending list of uuids: ')[1]
                logger.info("Succeeded to get guest uuid.list from rhsm.log.")
            elif "Sending domain info" in output:
                log_uuid_list = output.split('Sending domain info: ')[1]
                logger.info("Succeeded to get guest uuid.list from rhsm.log.")    
            else:
                raise FailException("Failed to get guest %s uuid.list from rhsm.log" % guestname)
            loglist = eval(log_uuid_list[:log_uuid_list.rfind("]\n") + 1].strip())
            for item in loglist:
                if item['guestId'] == guestuuid:
                    attr_status = item['attributes']['active']
                    logger.info("guest's active status is %s." % attr_status)
                    attr_type = item['attributes']['virtWhoType']
                    logger.info("guest virtwhotype is %s." % attr_type)
                    attr_hypertype = item['attributes']['hypervisorType']
                    logger.info("guest hypervisortype is %s." % attr_hypertype)
                    attr_state = item['state']
                    logger.info("guest state is %s." % attr_state)
            if guestname != "" and (guest_status == attr_status) and (guest_type in attr_type) and (guest_hypertype in attr_hypertype) and (guest_state == attr_state):
                logger.info("successed to check guest %s attribute" % guestname)
            else:
                raise FailException("Failed to check guest %s attribute" % guestname)
        else:
            logger.error("Failed to get uuids in rhsm.log")
            self.SET_RESULT(1)

    def vw_check_message_in_rhsm_log(self, message, message_exists=True, rhsmlogpath='/var/log/rhsm', targetmachine_ip=""):
        ''' check whether given message exist or not in rhsm.log. '''
        rhsmlogfile = os.path.join(rhsmlogpath, "rhsm.log")
        cmd = "tail -3 %s " % rhsmlogfile
        ret, output = self.runcmd(cmd, "tail last 3 line in rhsm.log", targetmachine_ip)
        if ret == 0:
            if message_exists:
                if message in output:
                    logger.info("Succeeded to get message in rhsm.log: %s") % message
                else:
                    raise FailException("Failed to get message in rhsm.log: %s") % message
            else:
                if message not in output:
                    logger.info("Succeeded to check message not in rhsm.log: %s") % message
                else:
                    raise FailException("Failed to check message not in rhsm.log: %s") % message
        else:
            raise FailException("Failed to get rhsm.log")

    def get_poolid_by_SKU(self, sku, targetmachine_ip=""):
        ''' get_poolid_by_SKU '''
        availpoollist = self.sub_listavailpools(sku, targetmachine_ip)
        if availpoollist != None:
            for index in range(0, len(availpoollist)):
                if("SKU" in availpoollist[index] and availpoollist[index]["SKU"] == sku):
                    rindex = index
                    break
                elif("ProductId" in availpoollist[index] and availpoollist[index]["ProductId"] == sku):
                    rindex = index
                    break
            if "PoolID" in availpoollist[index]:
                poolid = availpoollist[rindex]["PoolID"]
            else:
                poolid = availpoollist[rindex]["PoolId"]
            return poolid
        else:
            raise FailException("Failed to subscribe to the pool of the product: %s - due to failed to list available pools." % sku)

    def get_uuid_list_in_rhsm_log(self, rhsmlogpath='/var/log/rhsm', targetmachine_ip=""):
        ''' check if the guest attributions is correctly monitored by virt-who. '''
        rhsmlogfile = os.path.join(rhsmlogpath, "rhsm.log")
        if self.get_os_serials(targetmachine_ip) == "7":
            cmd = "nohup tail -f -n 0 %s > /tmp/tail.rhsm.log 2>&1 &" % rhsmlogfile
            ret, output = self.runcmd(cmd, "generate nohup.out file by tail -f", targetmachine_ip)
            self.vw_restart_virtwho(targetmachine_ip)
            time.sleep(10)
            cmd = "killall -9 tail ; cat /tmp/tail.rhsm.log"
            ret, output = self.runcmd(cmd, "get log number added to rhsm.log", targetmachine_ip)
        else: 
            self.vw_restart_virtwho(targetmachine_ip)
            cmd = "tail -3 %s " % rhsmlogfile
            ret, output = self.runcmd(cmd, "check output in rhsm.log", targetmachine_ip)
        if ret == 0:
            ''' get guest uuid.list from rhsm.log '''
            if "Sending list of uuids: " in output:
                log_uuid_list = output.split('Sending list of uuids: ')[1]
                logger.info("Succeeded to get guest uuid.list from rhsm.log.")
            elif "Sending update to updateConsumer: " in output:
                log_uuid_list = output.split('Sending update to updateConsumer: ')[1]
                logger.info("Succeeded to get guest uuid.list from rhsm.log.")
            elif "Sending update in hosts-to-guests mapping: " in output:
                log_uuid_list = output.split('Sending update in hosts-to-guests mapping: ')[1].split(":")[1].strip("}").strip()
                logger.info("Succeeded to get guest uuid.list from rhsm.log.")
            elif "Sending domain info" in output:
                # log_uuid_list = output.split('Sending domain info: ')[1].split(":")[1].strip("}").strip()
                log_uuid_list = output.split('Sending domain info: ')[1].strip()
                logger.info("log_uuid_list is %s" % log_uuid_list)
                logger.info("Succeeded to get guest uuid.list from rhsm.log.")
            else:
                raise FailException("Failed to get guest uuid.list from rhsm.log")
            return log_uuid_list
        else:
            raise FailException("Failed to get uuid list in rhsm.log")

    def cal_virtwho_thread(self, targetmachine_ip=""):
            self.vw_restart_virtwho()
            time.sleep(1)
            self.vw_restart_virtwho()
            time.sleep(1)
            self.vw_restart_virtwho()
            time.sleep(1)
            cmd = "ps -ef | grep -v grep | grep virt-who |wc -l"
            ret, output = self.runcmd(cmd, "calculate virt-who thread", targetmachine_ip)
            if ret == 0:
                logger.info("Succeeded to calculate virt-who thread. virt-who thread is %s" % output)
                return output
            else:
                raise FailException("Test Failed - Failed to calculate virt-who thread")
