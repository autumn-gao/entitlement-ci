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
        self.cm_install_basetool(targetmachine_ip)
        # virt-who install via upstream
        github_url = get_exported_param("GITHUB_URL")
        cmd = "git clone %s; cd virt-who; make install" % github_url
        ret, output = self.runcmd(cmd, "install virt-who via upstream", targetmachine_ip)

    def set_virtwho_version(self, targetmachine_ip=None):
        self.cm_set_rpm_version("VIRTWHO_VERSION", "virt-who", targetmachine_ip)

    def sys_setup(self, targetmachine_ip=None):
        self.cm_install_basetool(targetmachine_ip)
        # system setup for virt-who testing
        cmd = "yum install -y virt-who"
        ret, output = self.runcmd(cmd, "install virt-who for virt-who testing", showlogger=False)
        if ret == 0:
            logger.info("Succeeded to setup system for virt-who testing.")
        else:
            raise FailException("Test Failed - Failed to setup system for virt-who testing.")

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

    def virtwho_cli(self, mode):
        # only return CLI for virt-who esx, remote libvirt, hyperv mode, don't run cli 
        if mode == "esx":
            esx_owner, esx_env, esx_server, esx_username, esx_password = self.get_esx_info()
            cmd = "virt-who --esx --esx-owner=%s --esx-env=%s --esx-server=%s --esx-username=%s --esx-password=%s" % (esx_owner, esx_env, esx_server, esx_username, esx_password)
        elif mode == "hyperv":
            hyperv_owner, hyperv_env, hyperv_server, hyperv_username, hyperv_password = self.get_hyperv_info()
            cmd = "virt-who --hyperv --hyperv-owner=%s --hyperv-env=%s --hyperv-server=%s --hyperv-username=%s --hyperv-password=%s" % (hyperv_owner, hyperv_env, hyperv_server, hyperv_username, hyperv_password)
        elif mode == "xen":
            xen_owner, xen_env, xen_server, xen_username, xen_password = self.get_xen_info()
            cmd = "virt-who --xen --xen-owner=%s --xen-env=%s --xen-server=%s --xen-username=%s --xen-password=%s" % (xen_owner, xen_env, xen_server, xen_username, xen_password)
        elif mode == "rhevm":
            rhevm_owner, rhevm_env, rhevm_username, rhevm_password = self.get_rhevm_info()
            rhevm_server = "https:\/\/" + get_exported_param("RHEVM_IP") + ":443"
            cmd = "virt-who --rhevm --rhevm-owner=%s --rhevm-env=%s --rhevm-server=%s --rhevm-username=%s --rhevm-password=%s" % (rhevm_owner, rhevm_env, rhevm_server, rhevm_username, rhevm_password)
        elif mode == "libvirt":
            libvirt_owner, libvirt_env, libvirt_username, libvirt_password = self.get_libvirt_info()
            libvirt_server = get_exported_param("REMOTE_IP")
            cmd = "virt-who --libvirt --libvirt-owner=%s --libvirt-env=%s --libvirt-server=%s --libvirt-username=%s --libvirt-password=%s" % (libvirt_owner, libvirt_env, libvirt_server, libvirt_username, libvirt_password)
        else:
            raise FailException("Failed to get virt-who comand line with %s mode" % mode)
        return cmd

    # run virt-who oneshot by cli, return the output
    def virtwho_oneshot(self, mode, targetmachine_ip=""):
        cmd = self.virtwho_cli(mode) + " -o -d "
        self.service_command("stop_virtwho", targetmachine_ip)
        ret, output = self.runcmd(cmd, "executing virt-who with one shot", targetmachine_ip)
#         self.service_command("restart_virtwho")
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

    def vw_restart_virtwho(self, targetmachine_ip=""):
        ''' restart virt-who service. '''
        cmd = "service virt-who restart"
        ret, output = self.runcmd(cmd, "restart virt-who", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to restart virt-who service.")
        else:
            raise FailException("Test Failed - Failed to restart virt-who service.")

    def check_virtwho_thread(self, number, targetmachine_ip=""):
        ''' check virt-who thread number '''
        cmd = "ps -ef | grep -v grep | grep virt-who | wc -l"
        ret, output = self.runcmd(cmd, "check virt-who thread", targetmachine_ip)
        if ret == 0 and int(output.strip()) == number:
            logger.info("Succeeded to check virt-who thread number is %s." % number)
        else:
            raise FailException("Test Failed - Failed to check virt-who thread number is %s." % number)

    def update_config_to_default(self, targetmachine_ip=""):
        ''' update virt-who configure file to default mode '''
        cmd = "sed -i -e 's/^.*VIRTWHO_DEBUG=.*/VIRTWHO_DEBUG=0/g' -e 's/^.*VIRTWHO_INTERVAL=.*/#VIRTWHO_INTERVAL=0/g' -e 's/^.*VIRTWHO_VDSM=.*/#VIRTWHO_VDSM=0/g' -e 's/^.*VIRTWHO_RHEVM=.*/#VIRTWHO_RHEVM=0/g' -e 's/^.*VIRTWHO_HYPERV=.*/#VIRTWHO_HYPERV=0/g' -e 's/^.*VIRTWHO_ESX=.*/#VIRTWHO_ESX=0/g' -e 's/^.*VIRTWHO_LIBVIRT=.*/#VIRTWHO_LIBVIRT=0/g' /etc/sysconfig/virt-who"
        ret, output = self.runcmd(cmd, "updating virt-who configure file to defualt", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to update virt-who configure file to defualt.")
        else:
            raise FailException("Failed to virt-who configure file to defualt.")

    def config_option_disable(self, option, targetmachine_ip=""):
        # comment option in /etc/sysconfig/virt-who if given option enabled
        cmd = "sed -i 's/^%s/#%s/' /etc/sysconfig/virt-who" % (option, option)
        (ret, output) = self.runcmd(cmd, "Disable %s in /etc/sysconfig/virt-who" % option, targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to disable %s." % option)
        else:
            raise FailException("Failed to disable %s." % option)

    def config_option_enable(self, option, targetmachine_ip=""):
        # uncomment option in /etc/sysconfig/virt-who if given option disabled
        cmd = "sed -i 's/#%s/%s/' /etc/sysconfig/virt-who" % (option, option)
        (ret, output) = self.runcmd(cmd, "Enable %s in /etc/sysconfig/virt-who" % option, targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to enable %s." % option)
        else:
            raise FailException("Failed to enable %s." % option)

    def config_option_setup_value(self, option, value="", targetmachine_ip=""):
        # setup value for option in /etc/sysconfig/virt-who
        self.config_option_enable(option, targetmachine_ip)
        cmd = "sed -i 's/^%s=.*/%s=%s/' /etc/sysconfig/virt-who" % (option, option, value)
        (ret, output) = self.runcmd(cmd, "set %s to %s" % (option, value), targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to set %s=%s" % (option, value))
        else:
            raise FailException("Failed to set %s=%s" % (option, value))

    def set_virtwho_sec_config(self, mode, targetmachine_ip=""):
        conf_file, conf_data = self.set_virtwho_d_data(mode, targetmachine_ip)
        self.set_virtwho_d_conf(conf_file, conf_data, targetmachine_ip)

    def set_virtwho_sec_config_with_keyvalue(self, mode, key, value, targetmachine_ip=""):
        conf_file, conf_data = self.set_virtwho_d_data(mode, targetmachine_ip)
        pattern = re.compile(r'%s=.*?(?=\n|$)' % key)
        self.set_virtwho_d_conf(conf_file, pattern.sub("%s=%s" % (key, value), conf_data), targetmachine_ip)

    def set_virtwho_d_data(self, mode, targetmachine_ip=""):
        # prepare virt_who.d data.
        conf_file = "/etc/virt-who.d/virt-who"
        if mode == "esx":
            virtwho_owner, virtwho_env, virtwho_server, virtwho_username, virtwho_password = self.get_esx_info()
        elif mode == "libvirt":
            virtwho_owner, virtwho_env, virtwho_username, virtwho_password = self.get_libvirt_info()
            virtwho_server = get_exported_param("REMOTE_IP")
        elif mode == "hyperv":
            virtwho_owner, virtwho_env, virtwho_server, virtwho_username, virtwho_password = self.get_hyperv_info()
        elif mode == "xen":
            virtwho_owner, virtwho_env, virtwho_server, virtwho_username, virtwho_password = self.get_xen_info()
        elif mode == "rhevm":
            virtwho_owner, virtwho_env, virtwho_username, virtwho_password = self.get_rhevm_info()
            virtwho_server = "https://" + get_exported_param("RHEVM_IP") + ":443"
        # set conf data for all mode
        conf_data = "[%s]\n"\
                    "type=%s\n"\
                    "server=%s\n"\
                    "username=%s\n"\
                    "password=%s\n"\
                    "owner=%s\n"\
                    "env=%s\n" % (mode, mode, virtwho_server, virtwho_username, virtwho_password, virtwho_owner, virtwho_env)
        return conf_file, conf_data

    def set_virtwho_d_conf(self, file_name, file_data, targetmachine_ip=""):
        cmd = "cat > %s <<EOF\n"\
                        "%s\n"\
                        "EOF" % (file_name, file_data)
        ret, output = self.runcmd(cmd, "create config file: %s" % file_name, targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to create config file: %s" % file_name)
        else:
            raise FailException("Test Failed - Failed to create config file %s" % file_name)

    def get_host_uuids_list(self, mode, targetmachine_ip=""):
        self.set_filter_host_parents(mode, "", targetmachine_ip)
        # run virt-who one-shot with above config
        cmd = "virt-who -o -d"
        ret, output = self.runcmd(cmd, "executing virt-who with -o -d", targetmachine_ip)
        if ret == 0 and output is not None:
            host_list = re.findall(r"(?<=')host-.*?(?=')", output, re.I)
            if len(host_list) > 0:
                logger.info("Succeeded to get host_uuids_list: %s" % host_list)
                return host_list
            else:
                raise FailException("Failed, no host uuids found.")
        else:
            raise FailException("Failed to execute virt-who with -o -d")
        # remove above /etc/virt-who.d/virt.esx
        self.unset_all_virtwho_d_conf(targetmachine_ip)

    def get_host_parents_list(self, mode, targetmachine_ip=""):
        self.set_filter_host_parents(mode, "", targetmachine_ip)
        # run virt-who one-shot with above config
        cmd = "virt-who -o -d"
        ret, output = self.runcmd(cmd, "executing virt-who with -o -d", targetmachine_ip)
        if ret == 0 and output is not None:
            domain_list = re.findall(r"(?<=')domain-.*?(?=')", output, re.I)
            if len(domain_list) > 0:
                # domain_list = ','.join(list(set(domain_list))).replace("'", "\"")
                logger.info("Succeeded to get host_parents_list: %s" % domain_list)
                return domain_list
            else:
                raise FailException("Failed, no domain host found.")
        else:
            raise FailException("Failed to execute virt-who with -o -d")
        # remove above /etc/virt-who.d/virt.esx
        self.unset_all_virtwho_d_conf(targetmachine_ip)

    def set_filter_host_uuids(self, mode, host_uuids, targetmachine_ip=""):
        conf_file, conf_data = self.set_virtwho_d_data(mode, targetmachine_ip)
        conf_data = conf_data + "filter_host_uuids=%s\n" % host_uuids
        self.set_virtwho_d_conf(conf_file, conf_data, targetmachine_ip)

    def set_exclude_host_uuids(self, mode, host_uuids, targetmachine_ip=""):
        conf_file, conf_data = self.set_virtwho_d_data(mode, targetmachine_ip)
        conf_data = conf_data + "exclude_host_uuids=%s\n" % host_uuids
        self.set_virtwho_d_conf(conf_file, conf_data, targetmachine_ip)

    def set_filter_exclude_host_uuids(self, mode, filter_host_uuids, exclude_host_uuids, targetmachine_ip=""):
        conf_file, conf_data = self.set_virtwho_d_data(mode, targetmachine_ip)
        conf_data = conf_data + "filter_host_uuids=%s\n" % filter_host_uuids + "exclude_host_uuids=%s\n" % exclude_host_uuids
        self.set_virtwho_d_conf(conf_file, conf_data, targetmachine_ip)

    def set_hypervisor_id_filter_host_uuids(self, mode, hypervisor_id, host_uuids, targetmachine_ip=""):
        conf_file, conf_data = self.set_virtwho_d_data(mode, targetmachine_ip)
        conf_data = conf_data + "hypervisor_id=%s\n" % hypervisor_id + "filter_host_uuids=%s\n" % host_uuids
        self.set_virtwho_d_conf(conf_file, conf_data, targetmachine_ip)

    def set_hypervisor_id_exclude_host_uuids(self, mode, hypervisor_id, host_uuids, targetmachine_ip=""):
        conf_file, conf_data = self.set_virtwho_d_data(mode, targetmachine_ip)
        conf_data = conf_data + "hypervisor_id=%s\n" % hypervisor_id + "exclude_host_uuids=%s\n" % host_uuids
        self.set_virtwho_d_conf(conf_file, conf_data, targetmachine_ip)

    def set_filter_host_parents(self, mode, host_parents, targetmachine_ip=""):
        conf_file, conf_data = self.set_virtwho_d_data(mode, targetmachine_ip)
        conf_data = conf_data + "filter_host_parents=%s\n" % host_parents
        self.set_virtwho_d_conf(conf_file, conf_data, targetmachine_ip)

    def set_exclude_host_parents(self, mode, host_parents, targetmachine_ip=""):
        conf_file, conf_data = self.set_virtwho_d_data(mode, targetmachine_ip)
        conf_data = conf_data + "exclude_host_parents=%s\n" % host_parents
        self.set_virtwho_d_conf(conf_file, conf_data, targetmachine_ip)

    def set_filter_exclude_host_parents(self, mode, filter_host_parents, exclude_host_parents, targetmachine_ip=""):
        conf_file, conf_data = self.set_virtwho_d_data(mode, targetmachine_ip)
        conf_data = conf_data + "filter_host_parents=%s\n" % filter_host_parents + "exclude_host_parents=%s\n" % exclude_host_parents
        self.set_virtwho_d_conf(conf_file, conf_data, targetmachine_ip)

    def set_filter_host_uuids_exclude_parents(self, mode, filter_host_uuids, exclude_host_parents, targetmachine_ip=""):
        conf_file, conf_data = self.set_virtwho_d_data(mode, targetmachine_ip)
        conf_data = conf_data + "filter_host_uuids=%s\n" % filter_host_uuids + "exclude_host_parents=%s\n" % exclude_host_parents
        self.set_virtwho_d_conf(conf_file, conf_data, targetmachine_ip)

    def set_exclude_host_uuids_filter_parents(self, mode, exclude_host_uuids, filter_host_parents, targetmachine_ip=""):
        conf_file, conf_data = self.set_virtwho_d_data(mode, targetmachine_ip)
        conf_data = conf_data + "exclude_host_uuids=%s\n" % exclude_host_uuids + "filter_host_parents=%s\n" % filter_host_parents
        self.set_virtwho_d_conf(conf_file, conf_data, targetmachine_ip)

    def set_hypervisor_id(self, mode, hypervisor_id, targetmachine_ip=""):
        conf_file, conf_data = self.set_virtwho_d_data(mode, targetmachine_ip)
        conf_data = conf_data + "hypervisor_id=%s\n" % hypervisor_id
        self.set_virtwho_d_conf(conf_file, conf_data, targetmachine_ip)

    def set_rhsm_user_pass(self, mode, rhsm_username, rhsm_password, targetmachine_ip=""):
        conf_file, conf_data = self.set_virtwho_d_data(mode, targetmachine_ip)
        conf_data = conf_data + "rhsm_username=%s\nrhsm_password=%s" % (rhsm_username, rhsm_password)
        self.set_virtwho_d_conf(conf_file, conf_data, targetmachine_ip)

    def set_encrypted_password(self, mode, encrypted_password, targetmachine_ip=""):
        conf_file, conf_data = self.set_virtwho_d_data(mode, targetmachine_ip)
        pattern = re.compile(r'password=.*?(?=\n|$)')
        self.set_virtwho_d_conf(conf_file, pattern.sub("encrypted_password=%s" % encrypted_password, conf_data), targetmachine_ip)

    def generate_fake_file(self, virtwho_mode, fake_file="/tmp/fake_file", targetmachine_ip=""):
        if "kvm" in virtwho_mode:
            cmd = "virt-who -p -d > %s" % fake_file
        elif "vdsm" in virtwho_mode:
            cmd = "virt-who -p -d --vdsm > %s" % fake_file
        else:
            cmd = self.virtwho_cli(virtwho_mode) + " -p -d > %s" % fake_file
        ret, output = self.runcmd(cmd, "Generate fake file in %s mode" % virtwho_mode, targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to generate fake file in %s mode" % virtwho_mode)
            return fake_file
        else:
            raise FailException("Failed to generate fake file in %s mode" % virtwho_mode)

    def set_fake_mode_conf(self, fake_file, is_hypervisor, virtwho_owner, virtwho_env, targetmachine_ip=""):
        conf_file = "/etc/virt-who.d/fake"
        conf_data = "[fake]\n"\
                    "type=fake\n"\
                    "file=%s\n"\
                    "is_hypervisor=%s\n"\
                    "owner=%s\n"\
                    "env=%s" % (fake_file, is_hypervisor, virtwho_owner, virtwho_env)
        self.set_virtwho_d_conf(conf_file, conf_data, targetmachine_ip)
        return conf_file

    def unset_virtwho_d_conf(self, file_name, targetmachine_ip=""):
        # delete configure file in /etc/virt-who.d/virt-who
        cmd = "rm -f %s" % file_name
        ret, output = self.runcmd(cmd, "run cmd: %s" % cmd, targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to remove %s" % file_name)
        else:
            raise FailException("Test Failed - Failed to remove %s" % file_name)

    def unset_all_virtwho_d_conf(self, targetmachine_ip=""):
        # delete all configure file in /etc/virt-who.d/virt-who
        cmd = "rm -f /etc/virt-who.d/*"
        ret, output = self.runcmd(cmd, "run cmd: %s" % cmd, targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to remove all configure file in /etc/virt-who.d/virt-who")
        else:
            raise FailException("Test Failed - Failed to remove all configure file in /etc/virt-who.d/virt-who")

    def run_virt_who_password(self, input_password, timeout=None):
    # Get encrypted password
        import paramiko
        remote_ip = get_exported_param("REMOTE_IP")
        username = "root"
        password = "red2015"
        # virt_who_password_cmd = "python /usr/share/virt-who/virtwhopassword.py"
        virt_who_password_cmd = "virt-who-password"
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
        if self.get_os_serials(targetmachine_ip) == "7":
            cmd = "service libvirtd restart"
            ret, output = self.runcmd(cmd, "restart libvirtd", targetmachine_ip)
            if ret == 0:
                logger.info("Succeeded to restart libvirtd service.")
            else:
                raise FailException("Test Failed - Failed to restart libvirtd")
        else:
            cmd = "service libvirtd restart"
            ret, output = self.runcmd(cmd, "restart libvirtd", targetmachine_ip)
            if ret == 0:
                logger.info("Succeeded to restart libvirtd service.")
            else:
                raise FailException("Test Failed - Failed to restart libvirtd")

    def vw_restart_libvirtd_vdsm(self, targetmachine_ip=""):
        ''' restart libvirtd service. '''
        if self.get_os_serials(targetmachine_ip) == "7":
            cmd = "service libvirtd restart"
            ret, output = self.runcmd(cmd, "restart libvirtd", targetmachine_ip)
            if ret == 0:
                logger.info("Succeeded to restart libvirtd service.")
            else:
                raise FailException("Test Failed - Failed to restart libvirtd")
        else:
            cmd = "initctl restart libvirtd"
            ret, output = self.runcmd(cmd, "restart libvirtd", targetmachine_ip)
            if ret == 0:
                logger.info("Succeeded to restart libvirtd service.")
            else:
                raise FailException("Failed to initctl restart libvirtd")

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

#     # check virt-who servcie status, rhel7:"active" "failed" "unknown", rhel6:"running" "stopped"
#     def check_virtwho_status(self, targetmachine_ip=""):
#         if self.get_os_serials(targetmachine_ip) == "7":
#             # will feedback "active" "failed" "unknow"
#             cmd = "systemctl is-active virt-who"
#             ret, output = self.runcmd(cmd, "check virt-who service by systemctl.", targetmachine_ip)
#             return output.strip()
#         else:
#             # will feedback "running" "stopped" "failed"
#             cmd = "service virt-who status"
#             ret, output = self.runcmd(cmd, "check virt-who service status by sysvinit", targetmachine_ip)
#             if "running" in output:
#                 return "running"
#             elif "stopped" in output:
#                 return "stopped"
#             else:
#                 return "failed"

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
            raise FailException("Failed to subscribe the guest to the bonus pool of the product: %s - due to failed to list available pools." % SKU_id)

    def sub_subscribe_to_bonus_pool(self, productid, guest_ip=""):
        ''' subscribe the registered guest to the corresponding bonus pool of the product: productid. '''
        availpoollistguest = self.sub_listavailpools(productid, guest_ip)
        if availpoollistguest != None:
            rindex = -1
            for index in range(0, len(availpoollistguest)):
                if("SKU" in availpoollistguest[index] and availpoollistguest[index]["SKU"] == productid and self.check_type_virtual(availpoollistguest[index]) and (self.check_temporary_virtual(availpoollistguest[index]) is True)):
                    rindex = index
                    break
                elif("ProductId" in availpoollistguest[index] and availpoollistguest[index]["ProductId"] == productid and self.check_type_virtual(availpoollistguest[index])and (self.check_temporary_virtual(availpoollistguest[index]) is True)):
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
        self.sub_refresh(targetmachine_ip)
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

    def sub_check_consumed_pool(self, sku_id, key="PoolID", targetmachine_ip=""):
        self.sub_refresh(targetmachine_ip)
        ''' Check consumed subpool exist or not, if it is exist, return consumed pool id. '''
        cmd = "subscription-manager list --consumed"
        ret, output = self.runcmd(cmd, "list consumed subscriptions then get cosumed pool id", targetmachine_ip)
        if ret == 0:
            if "No consumed subscription pools to list" not in output:
                if sku_id in output:
                    consumed_lines = self.__parse_avail_pools(output)
                    if consumed_lines != None:
                        for line in range(0, len(consumed_lines)):
                            if key is not None and key != "":
                                if consumed_lines[line]["SKU"] == sku_id:
                                    logger.info("Succeeded to get consumed subscription %s pool id is %s in %s" % (sku_id, consumed_lines[line][key], self.get_hg_info(targetmachine_ip)))
                                    return consumed_lines[line][key]
                elif sku_id not in output:
                    logger.info("Succeeded to check entitlements %s - the product '%s' is not subscribed now." % (self.get_hg_info(targetmachine_ip), sku_id))
                    return True
                else:
                    raise FailException("Failed to list consumed subscription %s - Not the right consumed subscription is listed!" % self.get_hg_info(targetmachine_ip))
            else:
                return True
                logger.info("There is no consumed subscription to list!")
        else:
            raise FailException("Failed to list consumed subscriptions.")

    def sub_check_bonus_pool_after_migate(self, before_poolid, after_poolid, targetmachine_ip=""):
        if after_poolid is True:
            logger.info("Success to check bonus pool has been revoke after migration in %s" % self.get_hg_info(targetmachine_ip))
        elif before_poolid not in after_poolid:
            logger.info("Success to check bonus pool has been updated after migration in %s" % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Failed to check bonus pool after migration in %s" % self.get_hg_info(targetmachine_ip))

    # check "subscription-manager list --consumed" key & value 
    def check_consumed_status(self, sku_id, key="", value="", targetmachine_ip=""):
        ''' check consumed entitlements status details '''
        cmd = "subscription-manager list --consumed"
        ret, output = self.runcmd(cmd, "list consumed subscriptions", targetmachine_ip)
        if ret == 0 and output is not None:
            consumed_lines = self.__parse_avail_pools(output)
            if consumed_lines != None:
                for line in range(0, len(consumed_lines)):
                    if key is not None and value is not None and key != "" and value != "":
                        if consumed_lines[line]["SKU"] == sku_id and consumed_lines[line][key] == value :
                            logger.info("Succeeded to list the right consumed subscription, %s=%s %s." % (key, value, self.get_hg_info(targetmachine_ip)))
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

    def check_temporary_virtual(self, pool_dict):
        if "SubscriptionType" in pool_dict.keys():
            TypeName = "SubscriptionType"
        if "temporary" in pool_dict[TypeName] or "Temporary" in pool_dict[TypeName]:
            logger.info("The sku is temporary sku")
            return False
        else:
            logger.info("The sku is not temporary sku")
            return True

    def check_bonus_exist(self, sku_id, bonus_quantity, targetmachine_ip="", bonus_exist=True):
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
                        if pool_list[item]["SKU"] == sku_id and self.check_type_virtual(pool_list[item]) and pool_list[item][SKU_Number] == bonus_quantity and (self.check_temporary_virtual(pool_list[item]) is True):
                            if bonus_exist:
                                logger.info("Succeeded to check the bonus pool %s exist, and bonus quantity is %s" % (sku_id, bonus_quantity))
                            else:
                                raise FailException("Failed to check the bonus pool %s exist, and bonus quantity is %s" % (sku_id, bonus_quantity))
                            return True
                    if not bonus_exist:
                        logger.info("Succeeded to check the bonus pool %s not exist" % sku_id)
                    else:
                        raise FailException("Failed to check the bonus pool %s not exist" % sku_id)
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

    def generate_tmp_log(self, checkcmd, tmp_file, waiting_time=0, targetmachine_ip=""):
        cmd = "tail -f -n 0 /var/log/rhsm/rhsm.log > %s 2>&1 &" % tmp_file
        self.runcmd(cmd, "generate nohup.out file by tail -f", targetmachine_ip)
        self.runcmd(checkcmd, "run checkcmd", targetmachine_ip)
        if waiting_time == 0:
            if "vdsmd" in checkcmd or "libvirtd" in checkcmd:
                time.sleep(120)
            elif "rhsmcertd" in checkcmd:
                time.sleep(100)
            elif "virsh" in checkcmd:
                time.sleep(5)
            else:
                time.sleep(20)
        else:
            time.sleep(waiting_time)
        self.kill_pid("tail", targetmachine_ip)

    def kill_pid(self, pid_name, destination_ip=""):
        cmd = "ps -ef | grep %s -i | grep -v grep | awk '{print $2}'" % pid_name
#         ret, output = self.runcmd(cmd, "start to check %s pid" %pid_name, destination_ip)
        ret, output = self.runcmd(cmd, "start to check pid", destination_ip)
        if ret == 0 and output is not None:
            pids = output.strip().split('\n')
            for pid in pids:
                kill_cmd = "kill -9 %s" % pid
                self.runcmd(kill_cmd, "kill %s pid %s" % (pid_name, pid), destination_ip)

    def kill_virt_who_pid(self, destination_ip=""):
        pid_name = "virtwho.py"
        self.kill_pid(pid_name, destination_ip)

    def vw_check_uuid(self, guestuuid, uuidexists=True, checkcmd="service virt-who restart", targetmachine_ip=""):
        ''' check if the guest uuid is correctly monitored by virt-who. '''
        tmp_file = "/tmp/tail.rhsm.log"
#         checkcmd = "service virt-who restart"
#         self.generate_tmp_log(tmp_file, targetmachine_ip)
        self.generate_tmp_log(checkcmd, tmp_file, targetmachine_ip=targetmachine_ip)
        cmd = "cat %s" % tmp_file
        ret, output = self.runcmd(cmd, "get temporary log generated", targetmachine_ip)
        if ret == 0:
            if "Sending list of uuids: " in output:
                log_uuid_list = output.split('Sending list of uuids: ')[1]
            elif "Sending update to updateConsumer: " in output:
                log_uuid_list = output.split('Sending list of uuids: ')[1]
            elif "Sending domain info" in output:
                log_uuid_list = output.split('Sending domain info: ')[1]
            elif "Domain info" in output:
                log_uuid_list = output.split('Domain info: ')[1]
            elif "Sending update in hosts-to-guests mapping" in output:
                log_uuid_list = output.split('Sending update in hosts-to-guests mapping: ')[1]
            else:
                raise FailException("Failed to get uuid list from %s." % tmp_file)
            logger.info("Succeeded to get guest uuid.list from %s." % tmp_file)
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
            raise FailException("Failed to get content of %s.") % tmp_file

    def vw_check_attr(self, guestname, active, virtWhoType, hypervisorType, state, guestuuid, rhsmlogpath='/var/log/rhsm', checkcmd="service virt-who restart", waiting_time=0, targetmachine_ip=""):
        ''' check if the guest attributions is correctly monitored by virt-who. '''
        tmp_file = "/tmp/tail.rhsm.log"
        self.generate_tmp_log(checkcmd, tmp_file, waiting_time, targetmachine_ip=targetmachine_ip)
        cmd = "cat %s" % tmp_file
        mapping_info = json.loads(''.join(self.vw_get_mapping_info(cmd, targetmachine_ip)))
        if virtWhoType == "libvirt" or virtWhoType == "vdsm":
            for guest in mapping_info:
                if guest["guestId"] == guestuuid:
                    attr_state = guest['state']
                    logger.info("Guest state is %s." % attr_state)
                    attr_status = guest['attributes']['active']
                    logger.info("Guest's active status is %s." % attr_status)
                    attr_type = guest['attributes']['virtWhoType']
                    logger.info("Guest virtwhotype is %s." % attr_type)
                    attr_hypertype = guest['attributes']['hypervisorType']
                    logger.info("Guest hypervisortype is %s." % attr_hypertype)
        else:
            for host in mapping_info.keys():
                for guest in mapping_info[host]:
                    if guest["guestId"] == guestuuid:
                        attr_state = guest['state']
                        logger.info("Guest state is %s." % attr_state)
                        attr_status = guest['attributes']['active']
                        logger.info("Guest's active status is %s." % attr_status)
                        attr_type = guest['attributes']['virtWhoType']
                        logger.info("Guest virtwhotype is %s." % attr_type)
                        attr_hypertype = guest['attributes']['hypervisorType']
                        logger.info("Guest hypervisortype is %s." % attr_hypertype)
        if guestname != "" and (active == attr_status) and (virtWhoType in attr_type) and (hypervisorType in attr_hypertype) and (state == attr_state):
            logger.info("successed to check guest %s attribute" % guestname)
        else:
            raise FailException("Failed to check guest %s attribute" % guestname)

#     def hypervisor_check_attr(self, hostuuid, guestname, guest_status, guest_type, guest_hypertype, guest_state, guestuuid, rhsmlogpath='/var/log/rhsm', checkcmd="service virt-who restart", targetmachine_ip=""):
#         ''' check if the guest attributions is correctly monitored by virt-who. '''
#         tmp_file = "/tmp/tail.rhsm.log"
#         self.generate_tmp_log(checkcmd, tmp_file, 0, targetmachine_ip=targetmachine_ip)
#         cmd = "cat %s" % tmp_file
#         ret, output = self.runcmd(cmd, "get log number added to rhsm.log", targetmachine_ip)
#         if ret == 0:
#             ''' get guest uuid.list from rhsm.log '''
#             if "Sending list of uuids: " in output:
#                 log_uuid_list = output.split('Sending list of uuids: ')[1]
#                 logger.info("Succeeded to get guest uuid.list from rhsm.log.")
#             elif "Sending update to updateConsumer: " in output:
#                 log_uuid_list = output.split('Sending list of uuids: ')[1]
#                 logger.info("Succeeded to get guest uuid.list from rhsm.log.")
#             elif "Sending domain info" in output:
#                 log_uuid_list = output.split('Sending domain info: ')[1]
#                 logger.info("Succeeded to get guest uuid.list from rhsm.log.")
# #             elif "Sending update in hosts-to-guests mapping"in output:
# #                 log_uuid_list = output.split('Sending update in hosts-to-guests mapping: ')[1]
# #                 logger.info("Succeeded to get guest uuid.list from rhsm.log.")
#             elif "Host-to-guest mapping" in output:
#                 log_uuid_list = output.split('Host-to-guest mapping: ')[1]
#                 logger.info("Succeeded to get guest uuid.list from rhsm.log.")
#             else:
#                 raise FailException("Failed to get guest %s uuid.list from rhsm.log" % guestname)
#             hostloc = log_uuid_list.find(hostuuid)
#             khrightloc = log_uuid_list.find("[", hostloc, -1)
#             khleftloc = log_uuid_list.find("]", hostloc, -1)
#             ulst = log_uuid_list[khrightloc:khleftloc + 1]
#             logger.info("ulst is %s" % ulst)
# #             loglist = eval(ulst[:ulst.rfind("]\n") + 1].strip())
#             loglist = eval(ulst[:ulst.rfind("]") + 1].strip())
#             logger.info("loglist is %s" % loglist)
# #             loglist = eval(log_uuid_list[:log_uuid_list.rfind("]\n") + 1].strip())
#             for item in loglist:
#                 if item['guestId'] == guestuuid:
#                     attr_status = item['attributes']['active']
#                     logger.info("guest's active status is %s." % attr_status)
#                     attr_type = item['attributes']['virtWhoType']
#                     logger.info("guest virtwhotype is %s." % attr_type)
#                     attr_hypertype = item['attributes']['hypervisorType']
#                     logger.info("guest hypervisortype is %s." % attr_hypertype)
#                     attr_state = item['state']
#                     logger.info("guest state is %s." % attr_state)
#             if guestname != "" and (guest_status == attr_status) and (guest_type in attr_type) and (guest_hypertype in attr_hypertype) and (guest_state == attr_state):
#                 logger.info("successed to check guest %s attribute" % guestname)
#             else:
#                 raise FailException("Failed to check guest %s attribute" % guestname)
#         else:
#             raise FailException("Failed to get uuids in rhsm.log")

    def vw_check_message(self, cmd, message, message_exists=True, cmd_retcode=0, targetmachine_ip=""):
        ''' check whether given message exist or not, if multiple check needed, seperate them via '|' '''
        ret, output = self.runcmd(cmd, "check message in output", targetmachine_ip)
        if ret == cmd_retcode:
            msg_list = message.split("|")
            if message_exists:
                for msg in msg_list:
                    # logger.info("----------------------%s" % msg)
                    # logger.info("----------------------%s" % output)
                    if msg in output:
                        logger.info("Succeeded to get message in %s output: '%s'" % (cmd, msg))
                    else:
                        raise FailException("Failed to get message in %s output: '%s'" % (cmd, msg))
            else:
                for msg in msg_list:
                    if msg not in output:
                        logger.info("Succeeded to check message not in %s output: '%s'" % (cmd, msg))
                    else:
                        raise FailException("Failed to check message not in %s output: '%s'" % (cmd, msg))
        else:
            raise FailException("Failed to excute virt-who cmd %s" % cmd)

    def vw_check_message_in_rhsm_log(self, message, message_exists=True, checkcmd="service virt-who restart", targetmachine_ip=""):
        ''' check whether given message exist or not in rhsm.log. if multiple check needed, seperate them via '|' '''
        tmp_file = "/tmp/tail.rhsm.log"
        self.generate_tmp_log(checkcmd, tmp_file, targetmachine_ip=targetmachine_ip)
        cmd = "cat %s" % tmp_file
        self.vw_check_message(cmd, message, message_exists, 0, targetmachine_ip)

    def vw_check_message_in_debug_cmd(self, cmd, message, message_exists=True, targetmachine_ip=""):
        ''' check whether given message exist or not in virt-who -d mode.
        if multiple check needed, seperate them via '|' such as: self.vw_check_message_in_debug_cmd(cmd, "DEBUG|ERROR")'''
        tmp_file = "/tmp/virt-who.cmd.log"
        cmd = "%s > %s 2>&1 &" % (cmd, tmp_file)
        self.runcmd(cmd, "generate %s to parse virt-who -d output info" % tmp_file, targetmachine_ip=targetmachine_ip)
        time.sleep(10)
        cmd = "cat %s" % tmp_file
        self.vw_check_message(cmd, message, message_exists, 0, targetmachine_ip)
        self.kill_pid("virt-who")

    def vw_get_mapping_info(self, cmd, targetmachine_ip=""):
        ret, output = self.runcmd(cmd, "run command to get mapping info", targetmachine_ip)
        if ret == 0 and output is not None and ("ERROR" not in output or "Unable to read cache" in output):
            if "Sending update in hosts-to-guests mapping: {" in output:
                logger.info("Found: Sending update in hosts-to-guests mapping")
                rex = re.compile(r'(?<=Sending update in hosts-to-guests mapping: ){.*?}\n+(?=201|$)', re.S)
            elif "Domain info: [" in output:
                logger.info("Found: Domain info")
                rex = re.compile(r'(?<=Domain info: )\[.*?\]\n+(?=201|$)', re.S)
            elif "Host-to-guest mapping: {" in output:
                logger.info("Found: Host-to-guest mapping")
                rex = re.compile(r'(?<=Host-to-guest mapping: ){.*?}\n+(?=201|$)', re.S)
            elif "Sending domain info: [" in output:
                logger.info("Found: Sending domain info")
                rex = re.compile(r'(?<=Sending domain info: )\[.*?\]\n+(?=201|$)', re.S)
            elif "Associations found: {" in output:
                logger.info("Found: Associations found")
                rex = re.compile(r'(?<=Associations found: ){.*?}\n+(?=201|$)', re.S)
            else:
                raise FailException("Failed to find hosts-to-guests mapping info in output data")
            mapping_info = rex.findall(output)
            logger.info("all hosts-to-guests mapping as follows: \n%s" % mapping_info)
            return mapping_info
        else:
            raise FailException("Failed to check, there is an error message found or no output data.")

    def vw_check_mapping_info_in_rhsm_log(self, host_uuid, guest_uuid="", checkcmd="service virt-who restart", uuid_exist=True, targetmachine_ip=""):
        tmp_file = "/tmp/tail.rhsm.log"
        self.generate_tmp_log(checkcmd, tmp_file, 0, targetmachine_ip=targetmachine_ip)
        cmd = "cat %s" % tmp_file
        mapping_info = ''.join(self.vw_get_mapping_info(cmd, targetmachine_ip))
        if uuid_exist == True:
            if (host_uuid in mapping_info if host_uuid != "" else True) and (guest_uuid in mapping_info if guest_uuid != "" else True):
                logger.info("Succeeded to check, can find host_uuid '%s' and guest_uuid '%s'" % (host_uuid, guest_uuid))
            else:
                raise FailException("Failed to check, can not find host_uuid '%s' and guest_uuid '%s'" % (host_uuid, guest_uuid))
        else:
            if (host_uuid not in mapping_info if host_uuid != "" else True) and (guest_uuid not in mapping_info if guest_uuid != "" else True):
                logger.info("Succeeded to check, no host_uuid '%s' and guest_uuid '%s' found." % (host_uuid, guest_uuid))
            else:
                raise FailException("Failed to check, should be no host_uuid '%s' and guest_uuid '%s' found." % (host_uuid, guest_uuid))

    def vw_check_mapping_info_number(self, cmd, mapping_num=1, targetmachine_ip=""):
        mapping_info = self.vw_get_mapping_info(cmd, targetmachine_ip)
        if len(mapping_info) == mapping_num:
            logger.info("Succeeded to check hosts-to-guests mapping info number as %s" % mapping_num)
        else:
            raise FailException("Failed to check hosts-to-guests mapping info number as %s" % mapping_num)

    def vw_check_mapping_info_number_in_debug_cmd(self, cmd, mapping_num=1, waiting_time=0, targetmachine_ip=""):
        tmp_file = "/tmp/virt-who.cmd.log"
        cmd = "%s > %s 2>&1 &" % (cmd, tmp_file)
        self.runcmd(cmd, "generate %s to parse virt-who -d output info" % tmp_file, targetmachine_ip)
        time.sleep(waiting_time)
        cmd = "cat %s" % tmp_file
        self.vw_check_mapping_info_number(cmd, mapping_num, targetmachine_ip)
        self.kill_pid("virt-who")

    def vw_check_mapping_info_number_in_rhsm_log(self, mapping_num=1, waiting_time=0, checkcmd="service virt-who restart", targetmachine_ip=""):
        tmp_file = "/tmp/tail.rhsm.log"
        self.generate_tmp_log(checkcmd, tmp_file, waiting_time, targetmachine_ip=targetmachine_ip)
        cmd = "cat %s" % tmp_file
        self.vw_check_mapping_info_number(cmd, mapping_num, targetmachine_ip)

    def vw_check_message_number(self, cmd, message, number, targetmachine_ip=""):
        ret, output = self.runcmd(cmd, "run command to get message", targetmachine_ip)
        if ret == 0 and output is not None and  "ERROR" not in output:
            rex = re.compile(r'%s' % message, re.S)
            message_list = rex.findall(output)
            logger.info("all message list as follows: \n%s" % message_list)
            if len(message_list) == number:
                logger.info("Succeeded to check message number as %s" % number)
            else:
                raise FailException("Failed to check message number as %s" % number)
            return message_list
        else:
            raise FailException("Failed to check, there is an error message found or no output data.")

    def vw_check_message_number_in_debug_cmd(self, cmd, message, msg_num=1, waiting_time=0, targetmachine_ip=""):
        tmp_file = "/tmp/virt-who.cmd.log"
        cmd = "%s > %s 2>&1 &" % (cmd, tmp_file)
        self.runcmd(cmd, "generate %s to parse virt-who -d output info" % tmp_file, targetmachine_ip)
        time.sleep(waiting_time)
        cmd = "cat %s" % tmp_file
        self.vw_check_message_number(cmd, message, msg_num, targetmachine_ip)
        self.kill_pid("virt-who")

    def vw_check_message_number_in_rhsm_log(self, message, msg_num=1, waiting_time=0, checkcmd="service virt-who restart", targetmachine_ip=""):
        tmp_file = "/tmp/tail.rhsm.log"
        self.generate_tmp_log(checkcmd, tmp_file, waiting_time, targetmachine_ip=targetmachine_ip)
        cmd = "cat %s" % tmp_file
        self.vw_check_message_number(cmd, message, msg_num, targetmachine_ip)

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
        ''' check if the guest uuid is correctly monitored by virt-who. '''
        tmp_file = "/tmp/tail.rhsm.log"
        checkcmd = "service virt-who restart"
#         self.generate_tmp_log(tmp_file, targetmachine_ip)
        self.generate_tmp_log(checkcmd, tmp_file, targetmachine_ip=targetmachine_ip)
        cmd = "cat %s" % tmp_file
        ret, output = self.runcmd(cmd, "get temporary log generated", targetmachine_ip)
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
            elif "Domain info" in output:
                # log_uuid_list = output.split('Sending domain info: ')[1].split(":")[1].strip("}").strip()
                log_uuid_list = output.split('Domain info: ')[1].strip()
                logger.info("log_uuid_list is %s" % log_uuid_list)
                logger.info("Succeeded to get guest uuid.list from rhsm.log.")
            else:
                raise FailException("Failed to get guest uuid.list from rhsm.log")
            return log_uuid_list
        else:
            raise FailException("Failed to get uuid list in rhsm.log")

    def hypervisor_check_uuid(self, hostuuid, guestuuid, rhsmlogpath='/var/log/rhsm', checkcmd="service virt-who restart", uuidexists=True, targetmachine_ip=""):
        tmp_file = "/tmp/tail.rhsm.log"
        self.generate_tmp_log(checkcmd, tmp_file, targetmachine_ip=targetmachine_ip)
        cmd = "cat %s" % tmp_file
        ret, output = self.runcmd(cmd, "get log number added to rhsm.log", targetmachine_ip)
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
#             elif "Sending update in hosts-to-guests mapping" in output:
#                 log_uuid_list = output.split('Sending update in hosts-to-guests mapping: ')[1]
#                 logger.info("Succeeded to get guest uuid.list from rhsm.log.")
            elif "Domain info" in output:
                log_uuid_list = output.split('Domain info: ')[1]
                logger.info("Succeeded to get guest uuid.list from rhsm.log.")
            elif "Host-to-guest mapping" in output:
                log_uuid_list = output.split('Host-to-guest mapping: ')[1]
                logger.info("Succeeded to get guest uuid.list from rhsm.log.")
            else:
                raise FailException("Failed to get uuid list from rhsm.log")
            hostloc = log_uuid_list.find(hostuuid)
            if hostloc >= 0:
                if uuidexists:
                    khrightloc = log_uuid_list.find("[", hostloc, -1)
                    khleftloc = log_uuid_list.find("]", hostloc, -1)
                    ulst = log_uuid_list[khrightloc:khleftloc - 1]
                    if guestuuid == "" and len(ulst) == 0:
                        logger.info("Succeeded to get none uuid list")
                    else:
                        if guestuuid in ulst:
                            logger.info("Succeeded to check guestuuid %s in host %s" % (guestuuid, hostuuid))
                        else:
                            raise FailException("Failed to check guestuuid %s in host %s" % (guestuuid, hostuuid))
                else:
                    khrightloc = log_uuid_list.find("[", hostloc, -1)
                    khleftloc = log_uuid_list.find("]", hostloc, -1)
                    ulst = log_uuid_list[khrightloc:khleftloc + 1]
                    if guestuuid not in ulst:
                        logger.info("Succeeded to check guestuuid %s not in host %s" % (guestuuid, hostuuid))
                    else:
                        raise FailException("Failed to check guestuuid %s not in log_uuid_list" % guestuuid)
            else:
                raise FailException("Failed to get rhsm.log")
        else:
            raise FailException("Test Failed - log file has problem, please check it !")

    def get_host_uuid(self, targetmachine_ip=""):
        cmd = "virsh capabilities"
        ret, output = self.runcmd(cmd, "Get hypervisor's capabilities", targetmachine_ip, showlogger=False)
        if ret == 0:
            logger.info("Succeeded to get hypervisor's capabilities on %s" % self.get_hg_info(targetmachine_ip))
            datalines = output.splitlines()
            for line in datalines:
                if "uuid" in line:
                    khrightloc = line.find("<uuid>")
                    khleftloc = line.find("</uuid>")
                    uuid = line[khrightloc + 6:khleftloc].strip()
                    logger.info("Success to get hypervisor's uuid %s" % uuid)
                    return uuid
        else:
            raise FailException("Failed to get hypervisor's capabilities on %s" % self.get_hg_info(targetmachine_ip))

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

    # parse rhevm-shell result to dict
    def get_key_rhevm(self, output, non_key_value, key_value, find_value, targetmachine_ip=""):
        pool_dict = {}
        if output is not "":
            datalines = output.splitlines()
            values1 = False
            values2 = False
            ERROR_VALUE = "-1"
            for line in datalines:
                line = line.strip()
                if line.find(non_key_value) == 0:
                    result_values1 = line[(line.find(':') + 1):].strip()
                    logger.info("Succeeded to find the non_key_value %s's result_values1 %s" % (non_key_value, result_values1))
                    values1 = True
                elif line.find(key_value) == 0:
                    result_values2 = line[(line.find(':') + 1):].strip()
                    logger.info("Succeeded to find the key_value %s's result_values2 %s" % (key_value, result_values2))
                    values2 = True
                elif (line == "") and (values2 == True) and (values1 == False):
                    pool_dict[result_values2] = ERROR_VALUE
                    values2 = False
                if (values1 == True) and (values2 == True):
                    pool_dict[result_values2] = result_values1
                    values1 = False
                    values2 = False
            if find_value in pool_dict:
                findout_value = pool_dict[find_value]
                if findout_value == ERROR_VALUE:
                    logger.info("Failed to get the %s's %s, no value" % (find_value, non_key_value))
                    return ERROR_VALUE
                else:
                    logger.info("Succeeded to get the %s's %s is %s" % (find_value, non_key_value, findout_value))
                    return findout_value
            else:
                raise FailException("Failed to get the %s's %s" % (find_value, non_key_value))
        else:
            raise FailException("Failed to run rhevm-shell cmd.")

    def run_paramiko_interact_sshkeygen(self, cmd, remote_ip, username, password, timeout=None):
        """Execute the given commands in an interactive shell."""
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(remote_ip, 22, username, password)
        channel = ssh.get_transport().open_session()
        channel.settimeout(600)
        channel.get_pty()
        channel.exec_command(cmd)
        output = ""
        while True:
            data = channel.recv(1048576)
            output += data
            logger.debug("output: %s" % data)
            if channel.send_ready():
                if data.strip().endswith('yes/no)?'):
                    logger.debug("interactive input: yes")
                    channel.send("yes" + '\n')
                if data.strip().endswith('\'s password:'):
                    logger.debug("interactive input: red2015")
                    channel.send("red2015" + '\n')
                if data.strip().endswith('[Foreman] Username:'):
                    logger.debug("interactive input: admin")
                    channel.send("admin" + '\n')
                if data.strip().endswith('[Foreman] Password for admin:'):
                    logger.debug("interactive input: admin")
                    channel.send("admin" + '\n')
                if data.strip().endswith('(/root/.ssh/id_rsa):'):
                    logger.debug("interactive input: enter")
                    channel.send('\n')
                if data.strip().endswith('y/n)?'):
                    logger.debug("interactive input: yes")
                    channel.send("y" + '\n')
                if data.strip().endswith('(empty for no passphrase):'):
                    logger.debug("empty for no passphrase input: enter")
                    channel.send('\n')
                if data.strip().endswith('same passphrase again:'):
                    logger.debug("input same passphrase again: enter")
                    channel.send('\n')
                if channel.exit_status_ready():
                    break
        if channel.recv_ready():
            data = channel.recv(1048576)
            output += data
        return channel.recv_exit_status(), output

    def run_interact_sshkeygen(self, cmd, targetmachine_ip, username, password, timeout=None, comments=True):
        ret, output = self.run_paramiko_interact_sshkeygen(cmd, targetmachine_ip, username, password, timeout)
        return ret, output

    def generate_ssh_key(self, targetmachine_ip=""):
        remote_ip_2 = get_exported_param("REMOTE_IP_2")
        remote_ip = get_exported_param("REMOTE_IP")
        username = "root"
        password = "red2015"
        # generate pub-key in host2, then copy the key to host1
        cmd = "ssh-keygen"
        ret, output = self.run_interact_sshkeygen(cmd, remote_ip_2, username, password)
        if ret == 0:
            logger.info("Succeeded to generate ssh-keygen.")
        else:
            raise FailException("Test Failed - Failed to generate ssh-keygen.")
        cmd = "ssh-copy-id -i ~/.ssh/id_rsa.pub %s" % remote_ip
        ret, output = self.run_interact_sshkeygen(cmd, remote_ip_2, username, password)
        if ret == 0:
            logger.info("Succeeded to scp id_rsa.pub to remote host")
        else:
            raise FailException("Test Failed - Failed to scp id_rsa.pub to remote host")
