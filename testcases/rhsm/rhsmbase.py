from utils import *
from testcases.base import Base
from utils.exception.failexception import FailException

class RHSMBase(Base):
    # ========================================================
    #       0. Basic Functions
    # ========================================================

    def check_ip(self, ip_address):
        pattern = r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
        if re.match(pattern, ip_address):
            return True
        else:
            return False

    def domain_to_ip(self, domain_name):
        cmd = "dig +short %s" % domain_name
        (ret, output) = self.runcmd(cmd, "unregister")
        return output.strip("\n").strip(" ")

    def restore_environment(self):
        self.sub_unregister()

    # ========================================================
    #       1. Keyword Functions
    # ========================================================
    def sub_autosubscribe(self, autosubprod):
        # cmd = "subscription-manager subscribe --auto"
        cmd = "subscription-manager attach --auto"
        (ret, output) = self.runcmd(cmd, "auto-subscribe")
        if ret == 0:
            if ("Subscribed" in output) and ("Not Subscribed" not in output):
                logger.info("It's successful to auto-subscribe.")
            else:
                raise FailException("Test Failed - Failed to auto-subscribe correct product.")
        else:
            raise FailException("Test Failed - Failed to auto-subscribe.")

    def sub_register(self, username, password, subtype=""):
        if subtype == "":
            cmd = "subscription-manager register --username=%s --password=%s" % (username, password)
        else:
            cmd = "subscription-manager register --type=%s --username=%s --password=%s" % (subtype, username, password)

        if self.sub_isregistered():
            logger.info("The system is already registered, need to unregister first!")
            cmd_unregister = "subscription-manager unregister"
            (ret, output) = self.runcmd(cmd_unregister, "unregister")
            if ret == 0:
                if ("System has been unregistered." in output) or ("System has been un-registered." in output):
                    logger.info("It's successful to unregister.")
                else:
                    logger.info("The system is failed to unregister, try to use '--force'!")
                    cmd += " --force"
        (ret, output) = self.runcmd(cmd, "register")
        if ret == 0:
            if ("The system has been registered with ID:" in output) or ("The system has been registered with id:" in output):
                logger.info("It's successful to register.")
            else:
                raise FailException("Test Failed - The information shown after registered is not correct.")
        else:
            raise FailException("Test Failed - Failed to register.")

    def sub_unregister(self):
        if self.sub_isregistered():
            cmd = "subscription-manager unregister"
            (ret, output) = self.runcmd(cmd, "unregister")
            if ret == 0:
                if ("System has been unregistered." in output) or ("System has been un-registered." in output):
                    logger.info("It's successful to unregister.")
                else:
                    raise FailException("Test Failed - The information shown after unregistered is not correct.")
            else:
                raise FailException("Test Failed - Failed to unregister.")
        else:
            self.sub_clean_local_data()
            logger.info("The system is not registered to server now.")

    def sub_clean_local_data(self):
        cmd = "subscription-manager clean"
        (ret, output) = self.runcmd(cmd, "clean local data")
        if ret == 0 and "All local data removed" in output:
            logger.info("Local data has been cleaned in the server now.")
        else:
            raise FailException("Test Failed - Failed to clean local data.")

    def sub_isregistered(self):
        cmd = "subscription-manager identity"
        (ret, output) = self.runcmd(cmd, "identity")
        if ret == 0:
            logger.info("The system is registered to server now.")
            return True
        else:
            logger.info("The system is not registered to server now.")
            if "has been deleted" in output:
                logger.info("the system is not registered to server but has local data!")
            return False

    def sub_checkidcert(self):
        cmd = "ls /etc/pki/consumer/"
        (ret, output) = self.runcmd(cmd, "listing the files in /etc/pki/consumer/")
        if ret == 0 and "cert.pem" in output and "key.pem" in output:
            logger.info("There are identity certs in the consumer directory.")
            return True
        else:
            logger.info("There is no identity certs in the consumer directory.")
            return False

    def sub_set_servicelevel(self, service_level):
        # set service-level
        cmd = "subscription-manager service-level --set=%s" % service_level
        (ret, output) = self.runcmd(cmd, "set service-level as %s" % service_level)
        if ret == 0 and "Service level set to: %s" % service_level in output:
            logger.info("It's successful to set service-level as %s" % service_level)
        else:
            raise FailException("Test Failed - Failed to set service-level as %s" % service_level)

    def sub_checkproductcert(self, productid):
        rctcommand = self.check_rct()
        if rctcommand:
            cmd = "for i in /etc/pki/product-default/*; do rct cat-cert $i; done"
        else:
            cmd = "for i in /etc/pki/product-default/*; do openssl x509 -text -noout -in $i; done"
        (ret, output) = self.runcmd(cmd, "checking product cert")
        if ret == 0:
            if ("1.3.6.1.4.1.2312.9.1.%s" % productid in output) or ("ID: %s" % productid in output and "Path: /etc/pki/product-default/%s.pem" % productid in output):
                logger.info("The product cert is verified.")
            else:
                raise FailException("Test Failed - The product cert is not correct.")
        else:
            raise FailException("Test Failed - Failed to check product cert.")

    def check_rct(self):
        cmd = "rct cat-cert --help"
        (ret, output) = self.runcmd(cmd, "run rct cat-cert --help")
        if ret == 0:
            logger.info("rct cat-cert command can be used in the system")
            return True
        else:
            logger.info("rct cat-cert command can not be used in the system")
            return False

    def sub_unsubscribe(self):
        cmd = "subscription-manager unsubscribe --all"
        (ret, output) = self.runcmd(cmd, "unsubscribe")
        expectout = "This machine has been unsubscribed from"
        expectoutnew = "subscription removed from this system."
        expectout5101 = "subscription removed at the server."
        expectout5102 = "local certificate has been deleted."
        if ret == 0:
            if output.strip() == "" or (((expectout5101 in output) and (expectout5102 in output)) or expectout in output or expectoutnew in output):
                logger.info("It's successful to unsubscribe.")
            else:
                raise FailException("Test Failed - The information shown after unsubscribed is not correct.")
        else:
            raise FailException("Test Failed - Failed to unsubscribe.")

    def sub_getcurrentversion(self):
        version = None
        platform = None
        # get version
        cmd = "uname -r | awk -F \"el\" '{print substr($2,1,1)}'"
        (ret, output) = self.runcmd(cmd, showlogger=False)
        if ret == 0:
            version = output.strip("\n").strip(" ")
            logger.info("It's successful to get system version.")
        else:
            logger.info("It's failed to get system version.")
        # get paltform
        cmd = "lsb_release -i"
        (ret, output) = self.runcmd(cmd, showlogger=False)
        if ret == 0:
            platform = output.split("Enterprise")[1].strip(" ")
            logger.info("It's successful to get system platform")
        else:
            logger.info("It's failed to get system platform.")
        currentversion = version + platform
        return currentversion
    
    def sub_list_availablepool_list(self):
        cmd = "subscription-manager list --available | grep 'Pool ID:'"
        (ret, output) = self.runcmd(cmd)
        if ret == 0:
            if "no available subscription pools to list" not in output.lower():
                poollist=output.strip().split("\n")
                for i in range(len(poollist)):
                    poollist[i]=poollist[i].strip("Pool ID:             ")
                return poollist
                
    # Check if specified pool is available
    def sub_listavailpools(self, productid):
        cmd = "subscription-manager list --available"
        (ret, output) = self.runcmd(cmd)
        if ret == 0:
            if "no available subscription pools to list" not in output.lower():
                if productid in output:
                    logger.info("The right available pools are listed successfully.")
                    pool_list = self.__parse_listavailable_output(output)
                    return pool_list
                else:
                    raise FailException("Not the right available pools are listed!")
            else:
                logger.info("There is no Available subscription pools to list!")
                return None
        else:
            raise FailException("Test Failed - Failed to list available pools.")

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

    def get_subscription_serialnumlist(self):
        cmd = "ls /etc/pki/entitlement/ | grep -v key.pem"
        (ret, output) = self.runcmd(cmd, "list all certificates in /etc/pki/entitlement/")
        ent_certs = output.splitlines()
        serialnumlist = [line.replace('.pem', '') for line in ent_certs]
        return serialnumlist

    def get_entitlementcerts_list(self):
        rctcommand = self.check_rct()
        if rctcommand == True:
            cmd = "ls /etc/pki/entitlement/ | grep -v key.pem"
            (ret, output) = self.runcmd(cmd, "get entitlement certs list")
            if ret == 0:
                return output
            else:
                raise FailException("Test Failed - Failed to list entitlement certs list.")

    def sub_checkentitlementcerts(self, productid):
        rctcommand = self.check_rct()
        if rctcommand == True:
            cmd = "for i in $(ls /etc/pki/entitlement/ | grep -v key.pem); do rct cat-cert /etc/pki/entitlement/$i; done | grep %s" % (productid)
        else:
            cmd = "for i in $(ls /etc/pki/entitlement/ | grep -v key.pem); do openssl x509 -text -noout -in /etc/pki/entitlement/$i; done | grep %s" % (productid)
        (ret, output) = self.runcmd(cmd, "check entitlement certs")
        if ret == 0:
            if productid in output:
                logger.info("It's successful to check entitlement certificates.")
            else:
                raise FailException("Test Failed - The information shown entitlement certificates is not correct.")
        else:
            raise FailException("Test Failed - Failed to check entitlement certificates.")

    def sub_isconsumed(self, autosubprod):
        cmd = "subscription-manager list --consumed"
        (ret, output) = self.runcmd(cmd, "listing consumed subscriptions")
        if ret == 0 and autosubprod in output.strip() or 'Pool ID' in output:
            logger.info("The subscription of the product is consumed.")
            return True
        else:
            logger.info("The subscription of the product is not consumed.")
            return False

    def sub_get_consumerid(self):
        consumerid = ''
        if self.sub_isregistered():
            cmd = "subscription-manager identity"
            (ret, output) = self.runcmd(cmd, "get consumerid")
            if ret == 0 and ("system identity:" in output or "Current identity" in output):
                consumerid_gain = output.split('\n')
                consumerid_line_split = (consumerid_gain[0]).split(":")
                consumerid = (consumerid_line_split[1]).strip()
                logger.info("consumerid is gained successfully!")
            else:
                raise FailException("Test Failed - Failed to get subscription-manager identity")
        return consumerid

    # Check if specified pool is available
    def sub_listallavailpools(self, productid):
        cmd = "subscription-manager list --available --all"
        (ret, output) = self.runcmd(cmd, "listing available pools")
        if ret == 0:
            if "no available subscription pools to list" not in output.lower():
                if productid in output:
                    logger.info("The right available pools are listed successfully.")
                    pool_list = self.parse_listavailable_output(output)
                    return pool_list
                else:
                    raise FailException("Not the right available pools are listed!")
            else:
                logger.info("There is no Available subscription pools to list!")
                return None
        else:
            raise FailException("Test Failed - Failed to list all available pools.")

    def parse_listavailable_output(self, output):
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

    def sam_remote_create_org(self, samhostip, orgname):
        # create organization with orgname
        cmd = "headpin -u admin -p admin org create --name=%s" % (orgname)
        (ret, output) = self.runcmd_sam(cmd, '', samhostip)
        if ret == 0 and "Successfully created org" in output:
            logger.info("It's successful to create organization %s." % orgname)
        else:
            raise FailException("Test Failed - Failed to create organization %s." % orgname)

    def sam_remote_delete_org(self, samhostip, orgname):
        # delete an existing organization
        if self.sam_remote_is_org_exist(samhostip, orgname):
            cmd = "headpin -u admin -p admin org delete --name=%s" % (orgname)
            (ret, output) = self.runcmd_sam(cmd, '', samhostip)
            if ret == 0 and "Successfully deleted org" in output:
                logger.info("It's successful to delete organization %s." % orgname)
            else:
                raise FailException("Test Failed - Failed to delete organization %s." % orgname)
        else:
            logger.info("Org %s to be deleted does not exist." % (orgname))

    def sam_remote_is_org_exist(self, samhostip, orgname):
        # check an organization existing or not
        cmd = "headpin -u admin -p admin org list"
        (ret, output) = self.runcmd_sam(cmd, '', samhostip)
        if ret == 0 and orgname in output:
            logger.info("Organization %s exists." % orgname)
            return True
        else:
            logger.info("Organization %s does not exist." % orgname)
            return False

# All test focus on activationkey "qq", and it's attached pool '8ac20118533b351001533b3aa9c2020c'
    def sam_remote_activationkey_exist(self, samhostip, orgname):
        cmd = "headpin -u admin -p admin activation_key list --org=%s"%orgname
        (ret, output) = self.runcmd_sam(cmd, '', samhostip)
        if 'qq' in output.split():
            logger.info("activationkey qq exists. please check it's pool.")
            return True
        else:
            logger.info("activationkey qq does not exist. please create it.")
            return False

    def sam_remote_activationkey_check_pool(self, samhostip, orgname):
        cmd = "headpin -u admin -p admin activation_key info --org=%s --name=qq"%orgname
        (ret, output) = self.runcmd_sam(cmd, '', samhostip)
        if '8ac20118533b351001533b3aa9c2020c' in output.split():
            logger.info("activationkey qq is attached with pool '8ac20118533b351001533b3aa9c2020c'")
            return True
        else:
            logger.info("activationkey qq is not attached with pool '8ac20118533b351001533b3aa9c2020c'. please attach it.")
            return False

    def sam_remote_activationkey_attach_pool(self, samhostip, orgname):
        cmd = "headpin -u admin -p admin activation_key update --org=%s --name=qq --add_subscription=8ac20118533b351001533b3aa9c2020c"%orgname
        (ret, output) = self.runcmd_sam(cmd, '', samhostip)
        if ret == 0:
            logger.info("It's successful to attach pool 8ac20118533b351001533b3aa9c2020c to activationkey qq")
        else:
            raise FailException("Test Failed - Failed to attach pool to activationkey.")

    def sam_remote_activationkey_creation(self, samhostip, orgname):
        cmd = "headpin -u admin -p admin activation_key create --org=%s --name=qq"%orgname
        (ret, output) = self.runcmd_sam(cmd, '', samhostip)
        if ret == 0 and "Successfully created activation key" in output:
            logger.info("It's successful to create activationkey qq. please attach a pool for it.")
        else:
            raise FailException("Test Failed - Failed to create activationkey.")

    def set_system_time(self, system_time):
        cmd = 'date -s %s'%system_time
        (ret, output) = self.runcmd(cmd, "set system time expired")
        if ret ==0:
            logger.info("It's successful to set system time expired")
        else:
            raise FailException("Test Failed - failed to set system time expired")

    def restore_system_time(self):
        cmd = 'hwclock --hctosys'
        (ret, output) = self.runcmd(cmd, "restore system time")
        if ret ==0:
            logger.info("It's successful to restore system time")
        else:
            raise FailException("Test Failed - failed to restore system time")

    
    def parse_listconsumed_output(self, output):
        datalines = output.splitlines()
        data_list = []
        # split output into segmentations
        data_segs = []
        segs = []
        tmpline = ""
        '''
        for line in datalines:
        if ("Product Name:" in line) or ("ProductName" in line) or ("Subscription Name" in line):
              segs.append(line)
        elif segs:
             segs.append(line)
        if ("Expires:" in line) or ("Ends:" in line):
                data_segs.append(segs)
                segs = []
        '''
        # new way
        for line in datalines:
            if ("Product Name:" in line) or ("ProductName" in line) or ("Subscription Name" in line):
                tmpline = line
            elif line and ":" not in line:
                tmpline = tmpline + ' ' + line.strip()
            elif line and ":" in line:
                segs.append(tmpline)
                tmpline = line
            if ("Expires:" in line) or ("Ends:" in line):
                segs.append(tmpline)
                data_segs.append(segs)
                segs = []

        '''# handle item with multi rows
        for seg in data_segs:
                length = len(seg)
                for index in range(0, length):
                        if ":" not in seg[index]:
                                seg[index-1] = seg[index-1] + " " + seg[index].strip()
                for item in seg:
                        if ":" not in item:
                                seg.remove(item)
        '''
            # parse detail information
        for seg in data_segs:
            data_dict = {}
        for item in seg:
            keyitem = item.split(":")[0].replace(' ', '')
            valueitem = item.split(":")[1].strip()
            data_dict[keyitem] = valueitem
        data_list.append(data_dict)
        return data_list

    def restart_rhsmcertd(self):
        cmd = "service rhsmcertd restart"
        (ret, output) = self.runcmd(cmd, "restart rhsmcertd service")
        if ret == 0 and output != None:
            logger.info("It's successful to restart rhsmcertd service")
        else:
            raise FailException("Test Failed - Failed to restart rhsmcertd service.")

    def stop_rhsmcertd(self):
        cmd = "service rhsmcertd stop"
        (ret, output) = self.runcmd(cmd, "stop rhsmcertd service")
        if ret == 0 and "Redirecting to /bin/systemctl stop  rhsmcertd.service" in output:
            logger.info("It's successful to stop rhsmcertd service")
        else:
            raise FailException("Test Failed - Failed to restart rhsmcertd service.")

    # Return auto-attach interval
    def check_auto_attach_interval(self):
        cmd = "grep 'Auto-attach interval' /var/log/rhsm/rhsmcertd.log | tail -1"
        (ret, output) = self.runcmd(cmd, "get auto attach interval value")
        if ret == 0 and output != None:
            logger.info("It's successful to check interval")
            return output.split('interval: ')[1].split(' ')[0]
        else:
            raise FailException("Test Failed - Failed to check interval")

    def set_auto_attach_interval(self, interval):
        cmd = "sed -i '/autoAttachInterval/d' /etc/rhsm/rhsm.conf;echo 'autoAttachInterval=%s' >> /etc/rhsm/rhsm.conf" %(interval)
        (ret, output) = self.runcmd(cmd,'set interval')
        if ret == 0:
            logger.info("It's successful to set interval")
        else:
            raise FailException("Test Failed - Failed to set interval")

    # Return insecure value of rhsm.conf: 0 or 1
    def check_insecure_value(self):
        cmd = "grep insecure /etc/rhsm/rhsm.conf"
        (ret, output) = self.runcmd(cmd,'get insecure value')
        if ret == 0:
            logger.info("It's successful to get insecure value")
            return output.split('=')[1].strip()
        else:
            raise FailException("Test Failed - Failed to check interval")

    def set_insecure_value(self, insecurevalue):
        cmd="sed -i '/insecure/d' /etc/rhsm/rhsm.conf;sed -i '/# Set to 1 to disable certificate validation:/a\insecure = %s' /etc/rhsm/rhsm.conf"%insecurevalue
        (ret, output) = self.runcmd(cmd,'set insecure value')
        if ret == 0 and self.check_insecure_value() == insecurevalue:
            logger.info("It's successful to set insecure value")
        else:
            raise FailException("Test Failed - Failed to set insecure value")

    def check_and_backup_yum_repos(self):
        # check if yum.repos.d is empty
        cmd = "ls /etc/yum.repos.d | wc -l"
        (ret, output) = self.runcmd(cmd, "check if yum.repos.d is empty")
        if ret == 0:
            if output.strip() != '0':
                logger.info("It's successful to verify yum.repos.d is NOT empty. Backup is needed before testing")
                backuprepo = True
            else:
                logger.info("No need to back repos.")
                backuprepo = False
        else:
            raise FailException("Test Failed - Failed to check if yum.repos.d is empty.")
        if backuprepo == True:
            cmd = "rm -rf /root/backuprepo;mkdir /root/backuprepo; mv /etc/yum.repos.d/* /root/backuprepo/"
            (ret, output) = self.runcmd(cmd, "backup repo")
            if ret == 0:
                logger.info("It's successful to backup repo.")
            else:
                raise FailException("Test Failed - Failed to backuprepo.")
        else:
            logger.info("No need to back up repos")

    def restore_repos(self):
        cmd = "ls /root/backuprepo/*"
        (ret, output) = self.runcmd(cmd, "check if repos' backup is empty")
        if ret == 0:
            logger.info("The repos backup exist, and need restore")
            cmd = "mv /root/backuprepo/* /etc/yum.repos.d/"
            (ret, output) = self.runcmd(cmd, "restore repos back up")
            if ret == 0:
                logger.info("It's successful to restore repos")
            else:
                raise FailException("Test Failed - Failed to restore repo.")
        else:
            logger.info("no need to restore the repos")

    def clear_file_content(self, logfile):
        cmd = 'echo "" > %s'%logfile
        (ret, output) = self.runcmd(cmd, "clear file content")
        if ret == 0:
            logger.info("It's successful to clear contend of %s"%logfile)
        else:
            raise FailException("Test Failed - Failed to clear content.")

    def install_pkg(self, pkgname):
        cmd = "yum install -y %s"%pkgname
        (ret, output) = self.runcmd(cmd, "install package")
        if ret ==0:
            logger.info("It's successful to install package %s"%pkgname)
        else:
            raise FailException("Test Failed - Failed to install package %s"%pkgname)

    def remove_pkg(self, pkgname):
        cmd ="yum remove -y %s"%pkgname
        (ret, output) = self.runcmd(cmd, "remove package")
        if ret ==0:
            logger.info("It's successful to remove package %s"%pkgname)
        else:
            raise FailException("Test Failed - Failed to remove package %s"%pkgname)
