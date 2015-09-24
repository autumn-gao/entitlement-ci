from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from utils.exception.failexception import FailException
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants

class VDSMBase(VIRTWHOBase):
    def configure_rhel_host_bridge(self, targetmachine_ip=""):
        # Configure rhevm bridge on RHEL host
        network_dev = ""
        cmd = "ip route | grep `hostname -I | awk {'print $1'}` | awk {'print $3'}"
        ret, output = self.runcmd(cmd, "get network device", targetmachine_ip)
        if ret == 0:
            network_dev = output.strip()
            logger.info("Succeeded to get network device in %s." % self.get_hg_info(targetmachine_ip))
            if not "rhevm" in output:
                cmd = "sed -i '/^BOOTPROTO/d' /etc/sysconfig/network-scripts/ifcfg-%s; echo \"BRIDGE=rhevm\" >> /etc/sysconfig/network-scripts/ifcfg-%s;echo \"DEVICE=rhevm\nBOOTPROTO=dhcp\nONBOOT=yes\nTYPE=Bridge\"> /etc/sysconfig/network-scripts/ifcfg-br0" % (network_dev, network_dev)
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

    def get_rhevm_repo_file(self, targetmachine_ip=""):
        ''' wget rhevm repo file and add to rhel host '''
        cmd = "wget -P /etc/yum.repos.d/ http://10.66.100.116/projects/sam-virtwho/rhevm_repo/rhevm_7.2.repo"
        ret, output = self.runcmd(cmd, "wget rhevm repo file and add to rhel host", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to wget rhevm repo file and add to rhel host in %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Failed to wget rhevm repo file and add to rhel host in %s." % self.get_hg_info(targetmachine_ip))

    def conf_rhevm_shellrc(self, targetmachine_ip=""):
        ''' Config the env to login to rhevm_rhell '''
        tagetmachine_hostname = self.get_hostname(targetmachine_ip)
        cmd = "echo -e '[ovirt-shell]\nusername = admin@internal\nca_file = /etc/pki/ovirt-engine/ca.pem\nurl = https://%s:443/api\ninsecure = False\nno_paging = False\nfilter = False\ntimeout = -1\npassword = redhat' > /root/.rhevmshellrc" % tagetmachine_hostname
        ret, output = self.runcmd(cmd, "config rhevm_shell env on rhevm", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to config rhevm_shell env on rhevm in %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Failed to config rhevm_shell env on rhevm in %s." % self.get_hg_info(targetmachine_ip))

    # Add host to rhevm
    def rhevm_add_host(self, rhevm_host_name, rhevm_host_ip, targetmachine_ip):
        cmd = " rhevm-shell -c -E 'add host --name \"%s\" --address \"%s\" --root_password red2015'" % (rhevm_host_name, rhevm_host_ip)
        ret, output = self.runcmd(cmd, "add host to rhevm.", targetmachine_ip)
        if ret == 0:
            runtime = 0
            while True:
                cmd = " rhevm-shell -c -E 'list hosts --show-all'"
                ret, output = self.runcmd(cmd, "list hosts in rhevm.", targetmachine_ip)
                runtime = runtime + 1
                if ret == 0 and rhevm_host_name in output:
                    logger.info("Succeeded to list host %s." % rhevm_host_name)
                    status = self.get_key_rhevm(output, "status-state", "name", rhevm_host_name, targetmachine_ip)
                    if "up" in status:
                        logger.info("Succeeded to add new host %s to rhevm" % rhevm_host_name)
                        break
                    # elif "install_failed":
                    #    raise FailException("Failed to add host since status is %s" % (rhevm_host_name, status))
                    else :
                        logger.info("vm %s status-state is %s" % (rhevm_host_name, status))
                else:
                    raise FailException("Failed to list host %s in rhevm" % rhevm_host_name)
                time.sleep(10)
                if runtime > 120:
                    raise FailException("%s status has problem,status is %s." % (rhevm_host_name, status))
        else:
            raise FailException("Failed to add host %s to rhevm" % rhevm_host_name)
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

    # parse rhevm-result to dict
    def rhevm_info_dict(self, output, targetmachine_ip=""):
        rhevm_info_dict = {}
        if output is not "":
            datalines = output.splitlines()
            for line in datalines:
                if ":" in line:
                    key = line.strip().split(":")[0].strip()
                    value = line.strip().split(":")[1].strip()
                    print key + "==" + value
                    rhevm_info_dict[key] = value
            return rhevm_info_dict
        else:
            raise FailException("Failed to get output in rhevm-result file.")

    # wait for a while until expect status shown in /tmp/rhevm-result file
    def wait_for_status(self, cmd, status_key, status_value, targetmachine_ip, timeout=600):
        timout = 0
        while True:
            timout = timout + 1
            # cmd = "list hosts --show-all; exit"
            ret, output = self.runcmd(cmd, "list info updating in rhevm.", targetmachine_ip)
            rhevm_info = self.rhevm_info_dict(output)
            if status_value == "NotExist":
                if not status_key in rhevm_info.keys():
                    logger.info("Succeded to check %s not exist." % status_key)
                    return True
            elif status_key in rhevm_info.keys() and rhevm_info[status_key] == status_value:
                logger.info("Succeeded to get %s value %s in rhevm." % (status_key, status_value))
                return True
            elif status_key in rhevm_info.keys() and rhevm_info[status_key] != status_value:
                logger.info("Succeeded to remove %s" % status_value)
                return True
            elif timout > 60:
                logger.info("Time out, running rhevm-shell command in server failed.")
                return False
            else:
                logger.info("sleep 10 in wait_for_status.")
                time.sleep(10)

    # Add storagedomain in rhevm
    def add_storagedomain_to_rhevm(self, storage_name, attach_host_name, domaintype, storage_format, NFS_server, storage_dir, targetmachine_ip): 
        # Create storage nfs folder and active it
        cmd = "mkdir %s" % storage_dir
        self.runcmd(cmd, "create storage nfs folder", NFS_server)
        cmd = "sed -i '/%s/d' /etc/exports; echo '%s *(rw,no_root_squash)' >> /etc/exports" % (storage_dir.replace('/', '\/'), storage_dir)
        ret, output = self.runcmd(cmd, "set /etc/exports for nfs", NFS_server)
        if ret == 0:
            logger.info("Succeeded to add '%s *(rw,no_root_squash)' to /etc/exports file." % storage_dir)
        else:
            raise FailException("Failed to add '%s *(rw,no_root_squash)' to /etc/exports file." % storage_dir)
        cmd = "service nfs restart"
        ret, output = self.runcmd(cmd, "restarting nfs service", NFS_server)
        if ret == 0 :
            logger.info("Succeeded to restart service nfs.")
        else:
            raise FailException("Failed to restart service nfs.")

        cmd = "rhevm-shell -c -E 'add storagedomain --name \"%s\" --host-name \"%s\"  --type \"%s\" --storage-type \"nfs\" --storage_format \"%s\" --storage-address \"%s\" --storage-path \"%s\" --datacenter \"Default\"' " % (storage_name, attach_host_name, domaintype, storage_format, NFS_server, storage_dir)
        ret, output = self.runcmd(cmd, "Add storagedomain in rhevm.", targetmachine_ip)
        if self.wait_for_status("rhevm-shell -c -E 'list storagedomains --show-all' ", "status-state", "unattached", targetmachine_ip):
            logger.info("Succeeded to add storagedomains %s in rhevm." % storage_name)
        else:
            raise FailException("Failed to add storagedomains %s in rhevm." % storage_name)
        cmd = "rhevm-shell -c -E 'add storagedomain --name \"%s\" --host-name \"%s\"  --type \"%s\" --storage-type \"nfs\" --storage_format \"%s\" --storage-address \"%s\" --storage-path \"%s\" --datacenter-identifier \"Default\"' " % (storage_name, attach_host_name, domaintype, storage_format, NFS_server, storage_dir)
        ret, output = self.runcmd(cmd, "Attaches the storage domain to the Default data center.", targetmachine_ip)
        if self.wait_for_status("rhevm-shell -c -E 'list storagedomains --show-all' ", "status-state", "NotExist", targetmachine_ip):
            logger.info("Succeeded to maintenance storagedomains %s in rhevm." % storage_name)
        else:
            raise FailException("Failed to maintenance storagedomains %s in rhevm." % storage_name)

#     # activate storagedomain in rhevm
#     def activate_storagedomain(self, storage_name, targetmachine_ip): 
#         cmd = "rhevm-shell -c -E 'action storagedomain \"%s\" activate --datacenter-identifier \"Default\"' " % (storage_name)
#         ret, output = self.runcmd(cmd, "activate storagedomain in rhevm.", targetmachine_ip)
#         if "complete" in output:
#             if self.wait_for_status("rhevm-shell -c -E 'list storagedomains --show-all' ", "status-state", "NotExist", targetmachine_ip):
#         #if self.wait_for_status("rhevm-shell -c -E 'action storagedomain \"%s\" activate --datacenter-identifier \"Default\"' % (storage_name)", "status-state", "complete", targetmachine_ip):
#                 logger.info("Succeeded to activate storagedomains %s in rhevm." % storage_name)
#             else:
#                 raise FailException("Failed to list activate storagedomains %s in rhevm." % storage_name)
#         else:
#             raise FailException("Failed to activate storagedomains %s in rhevm." % storage_name)

    def install_virtV2V(self, targetmachine_ip=""):
        '''install virt-V2V'''
        cmd = "rpm -q virt-v2v"
        ret, output = self.runcmd(cmd, "check whether virt-V2V exist", targetmachine_ip)
        if ret == 0:
            logger.info("virt-V2V has already exist, needn't to install it.")
        else:
            logger.info("virt-V2V hasn't been installed.")
            cmd = "yum install virt-v2v -y"
            ret, output = self.runcmd(cmd, "install vdsm", targetmachine_ip)
            if ret == 0 and "Complete!" in output:
                logger.info("Succeeded to install virt-V2V.")
            else:
                raise FailException("Failed to install virt-V2V")

    def rhevm_define_guest(self, targetmachine_ip=""):
        ''' wget kvm img and xml file, define it in execute machine for converting to rhevm '''
        cmd = "test -d /home/rhevm_guest/ && echo presence || echo absence"
        ret, output = self.runcmd(cmd, "check whether guest exist", targetmachine_ip)
        if "presence" in output:
            logger.info("guest has already exist")
        else:
            # cmd = "wget -P /tmp/rhevm_guest/ http://10.66.100.116/projects/sam-virtwho/rhevm_guest/6.4_Server_x86_64"
            cmd = "wget -P /home/rhevm_guest/ http://10.66.100.116/projects/sam-virtwho/7.1_Server_x86_64"
            ret, output = self.runcmd(cmd, "wget kvm img file", targetmachine_ip, showlogger=False)
            if ret == 0:
                logger.info("Succeeded to wget kvm img file")
            else:
                raise FailException("Failed to wget kvm img file")
        # cmd = "wget -P /tmp/rhevm_guest/xml/ http://10.66.100.116/projects/sam-virtwho/rhevm_guest/xml/6.4_Server_x86_64.xml"
        cmd = "wget -P /home/rhevm_guest/xml/ http://10.66.100.116/projects/sam-virtwho/7.1_Server_x86_64.xml"
        ret, output = self.runcmd(cmd, "wget kvm xml file", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to wget xml img file")
        else:
            raise FailException("Failed to wget xml img file")
        cmd = "sed -i 's/^auth_unix_rw/#auth_unix_rw/' /etc/libvirt/libvirtd.conf"
        (ret, output) = self.runcmd(cmd, "Disable auth_unix_rw firstly in libvirtd config file", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to Disable auth_unix_rw.")
        else:
            raise FailException("Failed to Disable auth_unix_rw.")
        self.vw_restart_libvirtd()
        # cmd = "virsh define /tmp/rhevm_guest/xml/6.4_Server_x86_64.xml"
        cmd = "virsh define /home/rhevm_guest/xml/7.1_Server_x86_64.xml"
        ret, output = self.runcmd(cmd, "define kvm guest", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to define kvm guest")
        else:
            raise FailException("Failed to define kvm guest")

    def rhevm_undefine_guest(self, targetmachine_ip=""):
        # cmd = "virsh define /tmp/rhevm_guest/xml/6.4_Server_x86_64.xml"
        cmd = "virsh undefine 7.1_Server_x86_64.xml"
        ret, output = self.runcmd(cmd, "undefine kvm guest", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to undefine kvm guest")
        else:
            raise FailException("Failed to undefine kvm guest")
    # create_storage_pool
    def create_storage_pool(self, targetmachine_ip=""):
        ''' wget autotest_pool.xml '''
        cmd = "wget -P /tmp/ http://10.66.100.116/projects/sam-virtwho/autotest_pool.xml"
        ret, output = self.runcmd(cmd, "wget rhevm repo file and add to rhel host", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to wget autotest_pool.xml")
        else:
            raise FailException("Failed to wget autotest_pool.xml")
        # check whether pool exist, if yes, destroy it
        cmd = "virsh pool-list"
        ret, output = self.runcmd(cmd, "check whether autotest_pool exist", targetmachine_ip)
        if ret == 0 and "autotest_pool" in output:
            logger.info("autotest_pool exist.")
            cmd = "virsh pool-destroy autotest_pool"
            ret, output = self.runcmd(cmd, "destroy autotest_pool", targetmachine_ip)
            if ret == 0 and "autotest_pool destroyed" in output:
                logger.info("Succeeded to destroy autotest_pool")
            else:
                raise FailException("Failed to destroy autotest_pool")

        cmd = "virsh pool-create /tmp/autotest_pool.xml"
        ret, output = self.runcmd(cmd, "import vm to rhevm.")
        if ret == 0 and "autotest_pool created" in output:
            logger.info("Succeeded to create autotest_pool.")
        else:
            raise FailException("Failed to create autotest_pool.")

    # convert_guest_to_nfs with v2v tool
    def convert_guest_to_nfs(self, origin_machine_ip, NFS_server, NFS_export_dir, vm_hostname, targetmachine_ip=""):
        cmd = "virt-v2v -i libvirt -ic qemu+ssh://root@%s/system -o rhev -os %s:%s --network rhevm %s" % (origin_machine_ip, NFS_server, NFS_export_dir, vm_hostname)
        ret, output = self.runcmd_interact(cmd, "convert_guest_to_nfs with v2v tool", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to convert_guest_to_nfs with v2v tool")
        else:
            raise FailException("Failed to convert_guest_to_nfs with v2v tool")
        # convert the second guest
        cmd = "virt-v2v -i libvirt -ic qemu+ssh://root@%s/system -o rhev -os %s:%s --network rhevm %s -on \"Sec_%s\"" % (origin_machine_ip, NFS_server, NFS_export_dir, vm_hostname, vm_hostname)
        ret, output = self.runcmd_interact(cmd, "convert_guest_to_nfs with v2v tool", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to convert the second guest to nfs with v2v tool")
        else:
            raise FailException("Failed to convert the second guest to nfs with v2v tool")

    # Get storagedomain id 
    def get_domain_id(self, storagedomain_name, rhevm_host_ip):
        cmd = "rhevm-shell -c -E 'list storagedomains ' "
        ret, output = self.runcmd(cmd, "list storagedomains in rhevm.", rhevm_host_ip)
        if ret == 0 and storagedomain_name in output:
            logger.info("Succeeded to list storagedomains %s in rhevm." % storagedomain_name)
            storagedomain_id = self.get_key_rhevm(output, "id", "name", storagedomain_name, rhevm_host_ip)
            logger.info("%s id is %s" % (storagedomain_name, storagedomain_id))
            return storagedomain_id
        else :
            raise FailException("Failed to list storagedomains %s in rhevm." % storagedomain_name)

    # import guest to rhevm
    def import_vm_to_rhevm(self, guest_name, nfs_dir_for_storage_id, nfs_dir_for_export_id, rhevm_host_ip):
        # action vm "7.1_Server_x86_64" import_vm --storagedomain-identifier export_storage  --cluster-name Default --storage_domain-name data_storage
        # cmd = "rhevm-shell -c -E 'action vm \"%s\" import_vm --storagedomain-identifier %s --cluster-name Default --storage_domain-name %s' " % (guest_name, nfs_dir_for_export, nfs_dir_for_storage)
        cmd = "rhevm-shell -c -E 'action vm \"%s\" import_vm --storagedomain-identifier %s --cluster-name Default --storage_domain-id %s' " % (guest_name, nfs_dir_for_export_id, nfs_dir_for_storage_id)
        ret, output = self.runcmd(cmd, "import guest %s in rhevm." % guest_name, rhevm_host_ip)
        if ret == 0:
            runtime = 0
            while True:
                cmd = "rhevm-shell -c -E 'list vms --show-all' "
                ret, output = self.runcmd(cmd, "list VMS in rhevm.", rhevm_host_ip)
                runtime = runtime + 1
                if ret == 0 and guest_name in output:
                    logger.info("Succeeded to list vm %s." % guest_name)
                    status = self.get_key_rhevm(output, "status-state", "name", guest_name, rhevm_host_ip)
                    if "down" in status:
                        logger.info("Succeeded to import new vm %s to rhevm" % guest_name)
                        break
                    else :
                        logger.info("vm %s status-state is %s" % (guest_name, status))
                time.sleep(10)
                if runtime > 120:
                    raise FailException("%s status has problem,status is %s." % (guest_name, status))

# Start VM on RHEVM
    def rhevm_start_vm(self, rhevm_vm_name, rhevm_host_ip):
        cmd = "rhevm-shell -c -E 'action vm %s start'" % rhevm_vm_name
        ret, output = self.runcmd(cmd, "start vm on rhevm.", rhevm_host_ip)
        if ret == 0 and "cannot be accessed" not in output:
            runtime = 0
            while True:
                cmd = "rhevm-shell -c -E 'show vm %s'" % rhevm_vm_name
                ret, output = self.runcmd(cmd, "list vms in rhevm.", rhevm_host_ip)
                runtime = runtime + 1
                if ret == 0:
                    logger.info("Succeeded to list vms")
                    status = self.get_key_rhevm(output, "status-state", "name", rhevm_vm_name, rhevm_host_ip)
                    if status.find("up") >= 0 and status.find("powering") < 0 and output.find("guest_info-ips-ip-address") > 0:
                        logger.info("Succeeded to up vm %s in rhevm" % rhevm_vm_name)
                        time.sleep(20)
                        break
                    else :
                        logger.info("vm %s status-state is %s" % (rhevm_vm_name, status))
                    time.sleep(20)
                    if runtime > 50:
                        raise FailException("%s's status has problem,status is %s." % (rhevm_vm_name, status))
                else:
                    raise FailException("Failed to list vm %s" % rhevm_vm_name)
        else:
            raise FailException("Failed to start vm %s on rhevm" % rhevm_vm_name)

# Stop VM on RHEVM
    def rhevm_stop_vm(self, rhevm_vm_name, targetmachine_ip):
        cmd = "rhevm-shell -c -E 'action vm \"%s\" stop'" % rhevm_vm_name
        ret, output = self.runcmd(cmd, "stop vm on rhevm.", targetmachine_ip)
        if ret == 0:
            runtime = 0
            while True:
                cmd = "rhevm-shell -c -E 'show vm %s'" % rhevm_vm_name
                ret, output = self.runcmd(cmd, "list vms in rhevm.", targetmachine_ip)
                runtime = runtime + 1
                if ret == 0:
                    logger.info("Succeeded to list vms")
                    status = self.get_key_rhevm(output, "status-state", "name", rhevm_vm_name, targetmachine_ip)
                    if status.find("down") >= 0 and status.find("powering") < 0:
                        logger.info("Succeeded to stop vm %s in rhevm" % rhevm_vm_name)
                        break
                    else :
                        logger.info("vm %s status-state is %s" % (rhevm_vm_name, status))
                    time.sleep(20)
                    if runtime > 50:
                        raise FailException("%s's status has problem,status is %s." % (rhevm_vm_name, status))
                else:
                    raise FailException("Failed to list vm %s" % rhevm_vm_name)
        else:
            raise FailException("Failed to stop vm %s on rhevm" % rhevm_vm_name)

# Stop VM on RHEVM
    def rhevm_pause_vm(self, rhevm_vm_name, targetmachine_ip):
        cmd = "rhevm-shell -c -E 'action vm \"%s\" suspend'" % rhevm_vm_name
        ret, output = self.runcmd(cmd, "stop vm on rhevm.", targetmachine_ip)
        if ret == 0:
            runtime = 0
            while True:
                cmd = "rhevm-shell -c -E 'show vm %s'" % rhevm_vm_name
                ret, output = self.runcmd(cmd, "list vms in rhevm.", targetmachine_ip)
                runtime = runtime + 1
                if ret == 0:
                    logger.info("Succeeded to list vms")
                    status = self.get_key_rhevm(output, "status-state", "name", rhevm_vm_name, targetmachine_ip)
                    if status.find("suspended") >= 0 and status.find("saving_state") < 0:
                        logger.info("Succeeded to stop vm %s in rhevm" % rhevm_vm_name)
                        break
                    else :
                        logger.info("vm %s status-state is %s" % (rhevm_vm_name, status))
                    time.sleep(10)
                    if runtime > 20:
                        raise FailException("%s's status has problem,status is %s." % (rhevm_vm_name, status))
                else:
                    raise FailException("Failed to list vm %s" % rhevm_vm_name)
        else:
            raise FailException("Failed to stop vm %s on rhevm" % rhevm_vm_name)

    # get guest ip
    def rhevm_get_guest_ip(self, vm_name, targetmachine_ip):
        cmd = "rhevm-shell -c -E 'show vm %s'" % vm_name
        ret, output = self.runcmd(cmd, "list VMS in rhevm.", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to list vm %s." % vm_name)
            guestip = self.get_key_rhevm(output, "guest_info-ips-ip-address", "name", vm_name, targetmachine_ip)
            hostuuid = self.get_key_rhevm(output, "host-id", "name", vm_name, targetmachine_ip)
            if guestip is not "":
                logger.info("vm %s ipaddress is %s" % (vm_name, guestip))
                return (guestip, hostuuid)
            else:
                logger.error("Failed to gest the vm %s ipaddress" % vm_name)
        else:
            raise FailException("Failed to list VM %s." % vm_name) 

    def update_rhevm_vdsm_configure(self, interval_value, targetmachine_ip=""):
        ''' update virt-who configure file to vdsm mode /etc/sysconfig/virt-who. '''
        cmd = "sed -i -e 's/^.*VIRTWHO_DEBUG=.*/VIRTWHO_DEBUG=1/g' -e 's/^.*VIRTWHO_INTERVAL=.*/VIRTWHO_INTERVAL=%s/g' -e 's/^.*VIRTWHO_VDSM=.*/VIRTWHO_VDSM=1/g' /etc/sysconfig/virt-who" % interval_value
        ret, output = self.runcmd(cmd, "updating virt-who configure file", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to update virt-who configure file.")
        else:
            raise FailException("Failed to update virt-who configure file.")


    def vdsm_get_vm_uuid(self, vm_name, targetmachine_ip=""):
        ''' get the guest uuid. '''
        cmd = "rhevm-shell -c -E 'show vm %s'" % vm_name
        ret, output = self.runcmd(cmd, "list VMS in rhevm.", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to list vm %s." % vm_name)
            guestid = self.get_key_rhevm(output, "id", "name", vm_name, targetmachine_ip)
            if guestid is not "":
                logger.info("Succeeded to get guest %s id is %s" % (vm_name, guestid))
                return guestid
            else:
                logger.error("Failed to get guest %s id is %s" % (vm_name, guestid))
        else:
            raise FailException("Failed to list VM %s." % vm_name) 

    def vw_restart_vdsm(self, targetmachine_ip=""):
        ''' restart vdsmd service. '''
        cmd = "service vdsmd restart"
        ret, output = self.runcmd(cmd, "restart vdsmd", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to restart vdsmd service.")
        else:
            raise FailException("Test Failed - Failed to restart vdsmd")

    def rhel_rhevm_sys_setup(self, targetmachine_ip=""):
        RHEVM_IP = VIRTWHOConstants().get_constant("RHEVM_HOST")
        RHEL_RHEVM_GUEST_NAME = VIRTWHOConstants().get_constant("RHEL_RHEVM_GUEST_NAME")
        REMOTE_IP_NAME = self.get_hostname()
#         REMOTE_IP_2_NAME = self.get_hostname(get_exported_param("REMOTE_IP_2"))
        
        VIRTWHO_RHEVM_OWNER = VIRTWHOConstants().get_constant("VIRTWHO_RHEVM_OWNER")
        VIRTWHO_RHEVM_ENV = VIRTWHOConstants().get_constant("VIRTWHO_RHEVM_ENV")
        # VIRTWHO_RHEVM_SERVER = VIRTWHOConstants().get_constant("VIRTWHO_RHEVM_SERVER")
        VIRTWHO_RHEVM_USERNAME = VIRTWHOConstants().get_constant("VIRTWHO_RHEVM_USERNAME")
        VIRTWHO_RHEVM_PASSWORD = VIRTWHOConstants().get_constant("VIRTWHO_RHEVM_PASSWORD")

        NFSserver_ip = VIRTWHOConstants().get_constant("NFSserver_ip_test")
        nfs_dir_for_storage = VIRTWHOConstants().get_constant("NFS_DIR_FOR_storage")
        nfs_dir_for_export = VIRTWHOConstants().get_constant("NFS_DIR_FOR_export")

        # system setup for RHEL+RHEVM testing env
        cmd = "yum install -y @virtualization-client @virtualization-hypervisor @virtualization-platform @virtualization-tools @virtualization nmap net-tools bridge-utils rpcbind qemu-kvm-tools"
        ret, output = self.runcmd(cmd, "install kvm and related packages for kvm testing", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to setup system for virt-who testing in %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Test Failed - Failed to setup system for virt-who testing in %s." % self.get_hg_info(targetmachine_ip))
        self.configure_rhel_host_bridge(targetmachine_ip)
        self.get_rhevm_repo_file(targetmachine_ip)
        cmd = "yum install -y vdsm"
        ret, output = self.runcmd(cmd, "install vdsm and related packages", targetmachine_ip)
        if ret == 0:
            logger.info("Succeeded to install vdsm and related packages in %s." % self.get_hg_info(targetmachine_ip))
        else:
            raise FailException("Test Failed - Failed to install vdsm and related packages in %s." % self.get_hg_info(targetmachine_ip))
        self.stop_firewall(targetmachine_ip)
        #configure env on rhevm(add host,storage,guest)
        self.conf_rhevm_shellrc(RHEVM_IP)
        self.rhevm_add_host(REMOTE_IP_NAME, get_exported_param("REMOTE_IP"), RHEVM_IP)
        self.add_storagedomain_to_rhevm("data_storage", REMOTE_IP_NAME, "data", "v3", NFSserver_ip, nfs_dir_for_storage, RHEVM_IP)
        self.add_storagedomain_to_rhevm("export_storage", REMOTE_IP_NAME, "export", "v1", NFSserver_ip, nfs_dir_for_export, RHEVM_IP)
        self.rhevm_define_guest()
        self.create_storage_pool()
        self.install_virtV2V(RHEVM_IP)
        self.convert_guest_to_nfs(NFSserver_ip, nfs_dir_for_export, RHEL_RHEVM_GUEST_NAME, RHEVM_IP)
        self.rhevm_undefine_guest()
        data_storage_id = self.get_domain_id ("data_storage", RHEVM_IP)
        export_storage_id = self.get_domain_id ("export_storage", RHEVM_IP)
        self.import_vm_to_rhevm(RHEL_RHEVM_GUEST_NAME, data_storage_id, export_storage_id, RHEVM_IP)

    def rhel_rhevm_setup(self):
        SERVER_TYPE = get_exported_param("SERVER_TYPE")
        SERVER_IP = SERVER_HOSTNAME = SERVER_USER = SERVER_PASS = ""
        if SERVER_TYPE == "STAGE":
            SERVER_USER = VIRTWHOConstants().get_constant("STAGE_USER")
            SERVER_PASS = VIRTWHOConstants().get_constant("STAGE_PASS")
        else:
            SERVER_IP, SERVER_HOSTNAME, SERVER_USER, SERVER_PASS = self.get_server_info()

        # if host already registered, unregister it first, then configure and register it
        self.sub_unregister()
        self.configure_testing_server(SERVER_IP, SERVER_HOSTNAME)
        self.sub_register(SERVER_USER, SERVER_PASS)
        # update virt-who configure file
        self.update_rhevm_vdsm_configure(5)
        self.vw_restart_virtwho_new()
        # configure slave machine
        slave_machine_ip = get_exported_param("REMOTE_IP_2")
        if slave_machine_ip != None and slave_machine_ip != "":
            # if host already registered, unregister it first, then configure and register it
            self.sub_unregister(slave_machine_ip)
            self.configure_testing_server(SERVER_IP, SERVER_HOSTNAME, slave_machine_ip)
            self.sub_register(SERVER_USER, SERVER_PASS, slave_machine_ip)
            # update virt-who configure file
            self.update_rhevm_vdsm_configure(5, slave_machine_ip)
            self.vw_restart_virtwho_new(slave_machine_ip)


    def update_rhevm_vw_configure(self, rhevm_owner, rhevm_env, rhevm_server, rhevm_username, rhevm_password, background=1, debug=1):
        ''' update virt-who configure file /etc/sysconfig/virt-who for enable VIRTWHO_RHEVM'''
        cmd = "sed -i -e 's/^#VIRTWHO_DEBUG/VIRTWHO_DEBUG/g' -e 's/^#VIRTWHO_RHEVM/VIRTWHO_RHEVM/g' -e 's/^#VIRTWHO_RHEVM_OWNER/VIRTWHO_RHEVM_OWNERs/g' -e 's/^#VIRTWHO_RHEVM_ENV/VIRTWHO_RHEVM_ENV/g' -e 's/^#VIRTWHO_RHEVM_SERVER/VIRTWHO_RHEVM_SERVER/g' -e 's/^#VIRTWHO_RHEVM_USERNAME/VIRTWHO_RHEVM_USERNAME/g' -e 's/^#VIRTWHO_RHEVM_PASSWORD/VIRTWHO_RHEVM_PASSWORD/g' /etc/sysconfig/virt-who" 
        ret, output = self.runcmd(cmd, "updating virt-who configure file for enable VIRTWHO_RHEVM")
        if ret == 0:
            logger.info("Succeeded to enable VIRTWHO_RHEVM.")
        else:
            raise FailException("Test Failed - Failed to enable VIRTWHO_RHEVM.")