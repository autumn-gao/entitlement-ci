from utils import *
from testcases.virt_who_polarion.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException
from utils.libvirtAPI.Python.xmlbuilder import XmlBuilder

class KVMBase(VIRTWHOBase):
    # ========================================================
    #       KVM - system basic Functions
    # ========================================================
    def kvm_bridge_setup(self, targetmachine_ip=""):
        network_dev = ""
        cmd = "ip route | grep `hostname -I | awk {'print $1'}` | awk {'print $3'}"
        ret, output = self.runcmd(cmd, "get network device", targetmachine_ip)
        if ret == 0:
            network_dev = output.strip()
            logger.info("Succeeded to get network device in %s." % self.get_hg_info(targetmachine_ip))
            if not "switch" in output:
                cmd = "sed -i '/^BOOTPROTO/d' /etc/sysconfig/network-scripts/ifcfg-%s; echo \"BRIDGE=switch\" >> /etc/sysconfig/network-scripts/ifcfg-%s;echo \"DEVICE=switch\nBOOTPROTO=dhcp\nONBOOT=yes\nTYPE=Bridge\"> /etc/sysconfig/network-scripts/ifcfg-br0" % (network_dev, network_dev)
                ret, output = self.runcmd(cmd, "setup bridge for kvm testing", targetmachine_ip)
                if ret == 0:
                    logger.info("Succeeded to set /etc/sysconfig/network-scripts in %s." % self.get_hg_info(targetmachine_ip))
                else:
                    raise FailException("Test Failed - Failed to /etc/sysconfig/network-scripts in %s." % self.get_hg_info(targetmachine_ip))
                self.service_command("restart_network", targetmachine_ip)
            else:
                logger.info("Bridge already setup for virt-who testing, do nothing ...")
        else:
            raise FailException("Test Failed - Failed to get network device in %s." % self.get_hg_info(targetmachine_ip))

    def kvm_permission_setup(self, targetmachine_ip=""):
        cmd = "sed -i -e 's/#user = \"root\"/user = \"root\"/g' -e 's/#group = \"root\"/group = \"root\"/g' -e 's/#dynamic_ownership = 1/dynamic_ownership = 1/g' /etc/libvirt/qemu.conf"
        ret, output = self.runcmd(cmd, "setup kvm permission", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to set /etc/libvirt/qemu.conf in %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Test Failed - Failed to set /etc/libvirt/qemu.conf in %s." % self.get_hg_info(targetmachine_ip))

    def mount_images(self):
        ''' mount the images prepared '''
#         if get_exported_param("REMOTE_IP").startswith("hp-z220-"):
#             image_server = self.get_vw_cons("local_image_server")
#         else:
#             image_server = self.get_vw_cons("beaker_image_server")
        image_nfs_path = self.get_vw_cons("nfs_image_path")
        image_mount_path = self.get_vw_cons("local_mount_point")
#         cmd = "mkdir %s" % image_mount_path
#         self.runcmd(cmd, "create local images mount point")
#         cmd = "mkdir %s" % image_nfs_path
#         self.runcmd(cmd, "create local nfs images directory")
#         cmd = "mount -r %s %s; sleep 10" % (image_server, image_mount_path)
#         ret, output = self.runcmd(cmd, "mount images in host")
#         if ret == 0:
#             logger.info("Succeeded to mount images from %s to %s." % (image_server, image_mount_path))
#         else:
#             raise FailException("Failed to mount images from %s to %s." % (image_server, image_mount_path))
#         logger.info("Begin to copy guest images...")
#         cmd = "cp -n %s %s" % (os.path.join(image_mount_path, "ENT_TEST_MEDIUM/images/kvm/*"), image_nfs_path)
#         ret, output = self.runcmd(cmd, "copy all kvm images")
        # cmd = "umount %s" % (image_mount_path)
        # ret, output = self.runcmd(cmd, "umount images in host")
        self.cm_set_cp_image()
        cmd = "sed -i '/%s/d' /etc/exports; echo '%s *(rw,no_root_squash)' >> /etc/exports" % (image_nfs_path.replace('/', '\/'), image_nfs_path)
        ret, output = self.runcmd(cmd, "set /etc/exports for nfs")
        if ret == 0:
            logger.info("Succeeded to add '%s *(rw,no_root_squash)' to /etc/exports file." % image_nfs_path)
        else:
            raise FailException("Failed to add '%s *(rw,no_root_squash)' to /etc/exports file." % image_nfs_path)
        cmd = "service nfs restart"
        ret, output = self.runcmd(cmd, "restarting nfs service")
        if ret == 0 :
            logger.info("Succeeded to restart service nfs.")
        else:
            raise FailException("Failed to restart service nfs.")
        cmd = "rpc.mountd"
        ret, output = self.runcmd(cmd, "rpc.mountd")
        cmd = "showmount -e 127.0.0.1"
        ret, output = self.runcmd(cmd, "showmount")
        if ret == 0 and (image_nfs_path in output):
            logger.info("Succeeded to export dir '%s' as nfs." % image_nfs_path)
        else:
            raise FailException("Failed to export dir '%s' as nfs." % image_nfs_path)

    def mount_images_in_slave_machine(self, targetmachine_ip, imagenfspath, imagepath):
        ''' mount images in master machine to slave_machine. '''
        cmd = "test -d %s" % (imagepath)
        ret, output = self.runcmd(cmd, "check images dir exist", targetmachine_ip)
        if ret == 1:
            cmd = "mkdir -p %s" % (imagepath)
            ret, output = self.runcmd(cmd, "create image path in the slave_machine", targetmachine_ip)
            if ret == 0:
                logger.info("Succeeded to create imagepath in the slave_machine.")
            else:
                raise FailException("Failed to create imagepath in the slave_machine.")
        # mount image path of source machine into just created image path in slave_machine
        master_machine_ip = get_exported_param("REMOTE_IP")
        cmd = "mount %s:%s %s" % (master_machine_ip, imagenfspath, imagepath)
        ret, output = self.runcmd(cmd, "mount images in the slave_machine", targetmachine_ip)
        if ret == 0 or "is busy or already mounted" in output:
            logger.info("Succeeded to mount images in the slave_machine.")
        else:
            raise FailException("Failed to mount images in the slave_machine.")

    def __check_vm_available(self, guest_name, timeout=600, targetmachine_ip=""):
        terminate_time = time.time() + timeout
        guest_mac = self.__get_dom_mac_addr(guest_name, targetmachine_ip)
        self.__generate_ipget_file(targetmachine_ip)
        while True:
            guestip = self.__mac_to_ip(guest_mac, targetmachine_ip)
            if guestip != "" and (not "can not get ip by mac" in guestip):
                return guestip
            if terminate_time < time.time():
                raise FailException("Process timeout has been reached")
            logger.debug("Check guest IP, wait 10 seconds ...")
            time.sleep(10)

    def __generate_ipget_file(self, targetmachine_ip=""):
        generate_ipget_cmd = "wget -nc %s/ipget.sh -P /root/ && chmod 777 /root/ipget.sh" % self.get_vw_cons("data_folder")
        ret, output = self.runcmd(generate_ipget_cmd, "wget ipget file", targetmachine_ip)
        if ret == 0 or "already there" in output:
            logger.info("Succeeded to wget ipget.sh to /root/.")
        else:
            raise FailException("Test Failed - Failed to wget ipget.sh to /root/.")

    def getip_vm(self, guest_name, targetmachine_ip=""):
        guestip = self.__mac_to_ip(self.__get_dom_mac_addr(guest_name, targetmachine_ip), targetmachine_ip)
        if guestip != "" and (not "can not get ip by mac" in guestip):
            return guestip
        else:
            raise FailException("Test Failed - Failed to get ip of guest %s." % guest_name)

    def __get_dom_mac_addr(self, domname, targetmachine_ip=""):
        """
        Get mac address of a domain
        Return mac address on SUCCESS or None on FAILURE
        """
        cmd = "virsh dumpxml " + domname + " | grep 'mac address' | awk -F'=' '{print $2}' | tr -d \"[\'/>]\""
        ret, output = self.runcmd(cmd, "get mac address", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to get mac address of domain %s." % domname)
            return output.strip("\n").strip(" ")
        else:
            raise FailException("Test Failed - Failed to get mac address of domain %s." % domname)

    def __mac_to_ip(self, mac, targetmachine_ip=""):
        """
        Map mac address to ip, need nmap installed and ipget.sh in /root/ target machine
        Return None on FAILURE and the mac address on SUCCESS
        """
        if not mac:
            raise FailException("Failed to get guest mac ...")
        cmd = "sh /root/ipget.sh %s | grep -v nmap" % mac
        ret, output = self.runcmd(cmd, "check whether guest ip available", targetmachine_ip, showlogger=False)
        if ret == 0:
            logger.info("Succeeded to get ip address.")
            return output.strip("\n").strip(" ")
        else:
            raise FailException("Test Failed - Failed to get ip address.")

    # ========================================================
    #       KVM - virt-who test basic Functions
    # ========================================================
    def update_vw_configure(self, background=1, debug=1, targetmachine_ip=""):
        ''' update virt-who configure file /etc/sysconfig/virt-who. '''
        cmd = "sed -i -e 's/.*VIRTWHO_DEBUG=.*/VIRTWHO_DEBUG=%s/g' /etc/sysconfig/virt-who" % (debug)
        ret, output = self.runcmd(cmd, "updating virt-who configure file", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to update virt-who configure file.")
        else:
            raise FailException("Failed to update virt-who configure file.")

    def vw_get_uuid(self, guest_name, targetmachine_ip=""):
        ''' get the guest uuid. '''
        cmd = "virsh domuuid %s" % guest_name
        ret, output = self.runcmd(cmd, "get virsh domuuid", targetmachine_ip)
        if ret == 0:
            logger.info("get the uuid %s" % output)
        else:
            raise FailException("Failed to get the uuid")
        guestuuid = output[:-1].strip()
        return guestuuid

    def kvm_get_guest_ip(self, guest_name, targetmachine_ip=""):
        ''' get guest ip address in kvm host '''
        ipAddress = self.getip_vm(guest_name, targetmachine_ip)
        if ipAddress == None or ipAddress == "":
            raise FailException("Faild to get guest %s ip." % guest_name)
        else:
            return ipAddress

    def vw_define_all_guests(self, targetmachine_ip=""):
        guest_path = self.get_vw_cons("nfs_image_path")
        for guestname in self.get_all_guests_list(guest_path, targetmachine_ip):
            self.define_vm(guestname, os.path.join(guest_path, guestname), targetmachine_ip)

    def vw_undefine_all_guests(self, targetmachine_ip=""):
        guest_path = self.get_vw_cons("nfs_image_path")
        for guestname in self.get_all_guests_list(guest_path, targetmachine_ip):
            self.vw_undefine_guest(guestname, targetmachine_ip)

    def vw_define_guest(self, guestname, targetmachine_ip=""):
        guest_path = self.get_vw_cons("nfs_image_path")
        self.define_vm(guestname, os.path.join(guest_path, guestname), targetmachine_ip)

    def get_all_guests_list(self, guest_path, targetmachine_ip=""):
        cmd = "ls %s" % guest_path
        ret, output = self.runcmd(cmd, "get all guest in images folder", targetmachine_ip)
        if ret == 0 :
            guest_list = output.strip().split("\n")
            logger.info("Succeeded to get all guest list %s in %s." % (guest_list, guest_path))
            return guest_list
        else:
            raise FailException("Failed to get all guest list in %s." % guest_path)

    def vw_start_guests(self, guestname, targetmachine_ip=""):
        self.start_vm(guestname, targetmachine_ip)

    def vw_stop_guests(self, guestname, targetmachine_ip=""):
        self.shutdown_vm(guestname, targetmachine_ip)

    def define_vm(self, guest_name, guest_path, targetmachine_ip=""):
        cmd = "[ -f /root/%s.xml ]" % (guest_name)
        ret, output = self.runcmd(cmd, "check whether define xml exist", targetmachine_ip)
        if ret != 0 :
            logger.info("Generate guest %s xml." % guest_name)
            params = {"guestname":guest_name, "guesttype":"kvm", "source": "switch", "ifacetype" : "bridge", "fullimagepath":guest_path }
            xml_obj = XmlBuilder()
            domain = xml_obj.add_domain(params)
            xml_obj.add_disk(params, domain)
            xml_obj.add_interface(params, domain)
            dom_xml = xml_obj.build_domain(domain)
            self.define_xml_gen(guest_name, dom_xml, targetmachine_ip)
        cmd = "virsh define /root/%s.xml" % (guest_name)
        ret, output = self.runcmd(cmd, "define guest", targetmachine_ip)
        if ret == 0 or "already exists" in output:
            logger.info("Succeeded to define guest %s." % guest_name)
        else:
            raise FailException("Test Failed - Failed to define guest %s." % guest_name)
        self.list_vm(targetmachine_ip)

    def define_xml_gen(self, guest_name, xml, targetmachine_ip=""):
        cmd = "echo '%s' > /root/%s.xml" % (xml, guest_name)
        ret, output = self.runcmd(cmd, "write define xml", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to generate virsh define xml in /root/%s.xml " % guest_name)
        else:
            raise FailException("Test Failed - Failed to generate virsh define xml in /root/%s.xml " % guest_name)

    def define_xml_del(self, guest_xml, targetmachine_ip=""):
        cmd = "rm -f /root/%s.xml" % guest_xml
        ret, output = self.runcmd(cmd, "remove generated define xml", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to remove generated define xml: /root/%s.xml " % guest_xml)
        else:
            raise FailException("Test Failed - Failed to remove generated define xml: /root/%s.xml " % guest_xml)

    def list_vm(self, targetmachine_ip=""):
        cmd = "virsh list --all"
        ret, output = self.runcmd(cmd, "List all existing guests:", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to list all curent guest ")
        else:
            raise FailException("Test Failed - Failed to list all curent guest ")

    def start_vm(self, guest_name, targetmachine_ip=""):
        cmd = "virsh start %s" % (guest_name)
        ret, output = self.runcmd(cmd, "start guest" , targetmachine_ip)
        if ret == 0 or "already active" in output:
            logger.info("Succeeded to start guest %s." % guest_name)
        elif "Domain not found" in output:
            self.define_vm(guest_name, targetmachine_ip)
        else:
            raise FailException("Test Failed - Failed to start guest %s." % guest_name)
        return self.__check_vm_available(guest_name, targetmachine_ip=targetmachine_ip)

    def shutdown_vm(self, guest_name, targetmachine_ip=""):
        cmd = "virsh destroy %s" % (guest_name)
        ret, output = self.runcmd(cmd, "destroy guest", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to shutdown guest %s." % guest_name)
        else:
            raise FailException("Test Failed - Failed to shutdown guest %s." % guest_name)

    def pause_vm(self, guest_name, targetmachine_ip=""):
        ''' Pause a guest in host machine. '''
        cmd = "virsh suspend %s" % (guest_name)
        ret, output = self.runcmd(cmd, "pause guest", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to pause guest %s." % guest_name)
        else:
            raise FailException("Test Failed - Failed to pause guest %s." % guest_name)

    def resume_vm(self, guest_name, targetmachine_ip=""):
        ''' resume a guest in host machine. '''
        cmd = "virsh resume %s" % (guest_name)
        ret, output = self.runcmd(cmd, "resume guest", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to resume guest %s." % guest_name)
        else:
            raise FailException("Test Failed - Failed to pause guest %s.")

    def vw_migrate_guest(self, guestname, target_machine, origin_machine=""):
        ''' migrate a guest from source machine to target machine. '''
        uri = "qemu+ssh://%s/system" % target_machine
        cmd = "virsh migrate --live %s %s --undefinesource" % (guestname, uri)
        ret, output = self.runcmd_interact(cmd, "migrate guest from master to slave machine", origin_machine)
        if ret == 0:
            logger.info("Succeeded to migrate guest '%s' to %s." % (guestname, target_machine))
        else:
            raise FailException("Failed to migrate guest '%s' to %s." % (guestname, target_machine))

    def vw_undefine_guest(self, guestname, targetmachine_ip=""):
        ''' undefine guest in host machine. '''
        cmd = "virsh undefine %s" % guestname
        ret, output = self.runcmd(cmd, "undefine guest in %s" % targetmachine_ip, targetmachine_ip)
        if "Domain %s has been undefined" % guestname in output or "failed to get domain" in output:
            logger.info("Succeeded to undefine the guest '%s' in machine %s." % (guestname, targetmachine_ip))
        else:
            raise FailException("Failed to undefine the guest '%s' in machine %s." % (guestname, targetmachine_ip))

    def set_remote_libvirt_conf(self, virtwho_remote_server_ip, targetmachine_ip=""):
        VIRTWHO_LIBVIRT_OWNER, VIRTWHO_LIBVIRT_ENV, VIRTWHO_LIBVIRT_USERNAME, VIRTWHO_LIBVIRT_PASSWORD = self.get_libvirt_info()
        VIRTWHO_LIBVIRT_SERVER = virtwho_remote_server_ip
        cmd = "sed -i -e 's/.*VIRTWHO_DEBUG=.*/VIRTWHO_DEBUG=1/g' -e 's/.*VIRTWHO_LIBVIRT=.*/VIRTWHO_LIBVIRT=1/g' -e 's/.*VIRTWHO_LIBVIRT_OWNER=.*/VIRTWHO_LIBVIRT_OWNER=%s/g' -e 's/.*VIRTWHO_LIBVIRT_ENV=.*/VIRTWHO_LIBVIRT_ENV=%s/g' -e 's/.*VIRTWHO_LIBVIRT_SERVER=.*/VIRTWHO_LIBVIRT_SERVER=%s/g' -e 's/.*VIRTWHO_LIBVIRT_USERNAME=.*/VIRTWHO_LIBVIRT_USERNAME=%s/g' -e 's/.*VIRTWHO_LIBVIRT_PASSWORD=.*/VIRTWHO_LIBVIRT_PASSWORD=/g' /etc/sysconfig/virt-who" % (VIRTWHO_LIBVIRT_OWNER, VIRTWHO_LIBVIRT_ENV, VIRTWHO_LIBVIRT_SERVER, VIRTWHO_LIBVIRT_USERNAME)
        # set remote libvirt value
        ret, output = self.runcmd(cmd, "setting value for remote libvirt conf.", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to set remote libvirt value.")
        else:
            raise FailException("Test Failed - Failed to set remote libvirt value.")

    def clean_remote_libvirt_conf(self, targetmachine_ip=""):
        cmd = "sed -i -e 's/.*VIRTWHO_DEBUG=.*/VIRTWHO_DEBUG=1/g' -e 's/^.*VIRTWHO_INTERVAL=.*/#VIRTWHO_INTERVAL=0/g' -e 's/.*VIRTWHO_LIBVIRT=.*/#VIRTWHO_LIBVIRT=0/g' -e 's/.*VIRTWHO_LIBVIRT_OWNER=.*/#VIRTWHO_LIBVIRT_OWNER=/g' -e 's/.*VIRTWHO_LIBVIRT_ENV=.*/#VIRTWHO_LIBVIRT_ENV=/g' -e 's/.*VIRTWHO_LIBVIRT_SERVER=.*/#VIRTWHO_LIBVIRT_SERVER=/g' -e 's/.*VIRTWHO_LIBVIRT_USERNAME=.*/#VIRTWHO_LIBVIRT_USERNAME=/g' -e 's/.*VIRTWHO_LIBVIRT_PASSWORD=.*/#VIRTWHO_LIBVIRT_PASSWORD=/g' /etc/sysconfig/virt-who"
        # set remote libvirt value
        ret, output = self.runcmd(cmd, "Clean config of remote libvirt conf. reset to default", targetmachine_ip)
        if ret == 0:
            self.vw_restart_virtwho_new(targetmachine_ip)
            logger.info("Succeeded to reset to defualt config.")
        else:
            raise FailException("Test Failed - Failed to reset to defualt config.")

    def setup_libvirtd_config(self):
        cmd = "sed -i -e 's/^#listen_tls = 0/listen_tls = 0/g' -e 's/^#listen_tcp = 1/listen_tcp = 1/g' -e 's/^#auth_tcp = \"sasl\"/auth_tcp = \"sasl\"/g' -e 's/^#tcp_port = \"16509\"/tcp_port = \"16509\"/g' /etc/libvirt/libvirtd.conf"
        ret, output = self.runcmd(cmd, "setup_libvirtd_config")
        if ret == 0 :
            logger.info("Succeeded to setup_libvirtd_config.")
        else:
            raise FailException("Test Failed - Failed to setup_libvirtd_config.")

    def restore_libvirtd_config(self):
        cmd = "sed -i -e 's/^listen_tls = 0/#listen_tls = 0/g' -e 's/^listen_tcp = 1/#listen_tcp = 1/g' -e 's/^auth_tcp = \"sasl\"/#auth_tcp = \"sasl\"/g' -e 's/^tcp_port = \"16509\"/#tcp_port = \"16509\"/g' /etc/libvirt/libvirtd.conf"
        ret, output = self.runcmd(cmd, "restore_libvirtd_config")
        if ret == 0 :
            logger.info("Succeeded to restore_libvirtd_config.")
        else:
            raise FailException("Test Failed - Failed to restore_libvirtd_config.")

    # ========================================================
    #       KVM - test env set up function
    # ========================================================
    def kvm_setup(self):
        SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()
        # if host already registered, unregister it first, then configure and register it
        self.sub_unregister()
        self.configure_server(SERVER_IP, SERVER_HOSTNAME)
        self.sub_register(SERVER_USER, SERVER_PASS)
        # update virt-who configure file
        self.update_vw_configure()
        # restart virt-who service
        self.vw_restart_virtwho()
        # mount all needed guests
        self.mount_images()
        # add guests in host machine.
        self.vw_define_all_guests()
        # configure slave machine
        slave_machine_ip = get_exported_param("REMOTE_IP_2")
        if slave_machine_ip != None and slave_machine_ip != "":
            # if host already registered, unregister it first, then configure and register it
            self.sub_unregister(slave_machine_ip)
            self.configure_server(SERVER_IP, SERVER_HOSTNAME, slave_machine_ip)
            self.sub_register(SERVER_USER, SERVER_PASS, slave_machine_ip)
            image_nfs_path = self.get_vw_cons("nfs_image_path")
            self.mount_images_in_slave_machine(slave_machine_ip, image_nfs_path, image_nfs_path)
            self.update_vw_configure(slave_machine_ip)
            self.vw_restart_virtwho(slave_machine_ip)

    def kvm_sys_setup(self, targetmachine_ip=""):
        self.cm_install_basetool(targetmachine_ip)
        # system setup for virt-who testing
        cmd = "yum install -y @virtualization-client @virtualization-hypervisor @virtualization-platform @virtualization-tools @virtualization nmap net-tools bridge-utils rpcbind qemu-kvm-tools"
        ret, output = self.runcmd(cmd, "install kvm and related packages for kvm testing", targetmachine_ip, showlogger=False)
        if ret == 0:
            logger.info("Succeeded to setup system for virt-who testing in %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Test Failed - Failed to setup system for virt-who testing in %s." % self.get_hg_info(targetmachine_ip))
        self.kvm_bridge_setup(targetmachine_ip)
        self.kvm_permission_setup(targetmachine_ip)
        cmd = "service libvirtd start"
        ret, output = self.runcmd(cmd, "restart libvirtd service", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to start service libvirtd in %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Test Failed - Failed to start service libvirtd in %s." % self.get_hg_info(targetmachine_ip))
        self.stop_firewall(targetmachine_ip)

    def kvm_setup_arch(self):
        SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()
        # if host already registered, unregister it first, then configure and register it
        self.sub_unregister()
        self.configure_server(SERVER_IP, SERVER_HOSTNAME)
        self.sub_register(SERVER_USER, SERVER_PASS)
        # update virt-who configure file
        self.update_vw_configure()
        # restart virt-who service
        self.vw_restart_virtwho()

    def kvm_sys_setup_arch(self, targetmachine_ip=""):
        self.cm_install_basetool(targetmachine_ip)
        # system setup for virt-who testing
        cmd = "yum install -y @virtualization-client @virtualization-hypervisor @virtualization-platform @virtualization-tools @virtualization nmap net-tools bridge-utils rpcbind qemu-kvm-tools"
        ret, output = self.runcmd(cmd, "install kvm and related packages for kvm testing", targetmachine_ip, showlogger=False)
        if ret == 0:
            logger.info("Succeeded to setup system for virt-who testing in %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Test Failed - Failed to setup system for virt-who testing in %s." % self.get_hg_info(targetmachine_ip))
        cmd = "service libvirtd start"
        ret, output = self.runcmd(cmd, "restart libvirtd service", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to start service libvirtd in %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Test Failed - Failed to start service libvirtd in %s." % self.get_hg_info(targetmachine_ip))
        self.stop_firewall(targetmachine_ip)
