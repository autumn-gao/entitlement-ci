from utils import *
from testcases.base import Base
from utils.exception.failexception import FailException

class SAM_Install_Base(Base):

    def install_sam(self, compose, server_ip=None, server_user=None, server_passwd=None):
        self.__stop_iptables(server_ip, server_user, server_passwd)
        self.__set_selinux(server_ip, server_user, server_passwd)
#         self.__set_hosts_file(server_ip, server_user, server_passwd)
        # install sam via product cdn
        self.__auto_subscribe(server_ip, server_user, server_passwd)
        self.__enable_sam_repo(server_ip, server_user, server_passwd)
        # install sam via data server
        # self.__add_sam_repo(compose, server_ip, server_user, server_passwd)
        self.__install_katello(server_ip, server_user, server_passwd)
        self.__deploy_sam(server_ip, server_user, server_passwd)
        self.__import_manifest(server_ip, server_user, server_passwd)

    def install_satellite(self, compose, server_ip=None, server_user=None, server_passwd=None):
#         self.__stop_iptables(server_ip, server_user, server_passwd)
        self.__set_selinux(server_ip, server_user, server_passwd)
        self.__satellite_subscribe(server_ip, server_user, server_passwd)
        self.__add_satellite_repo(compose, server_ip, server_user, server_passwd)
        self.__install_satellite(server_ip, server_user, server_passwd)
        self.__deploy_satellite(server_ip, server_user, server_passwd)
        self.__import_manifest_satellite(server_ip, server_user, server_passwd)

    def install_satellite62(self, compose, server_ip=None, server_user=None, server_passwd=None):
#         self.__stop_iptables(server_ip, server_user, server_passwd)
        self.__set_selinux(server_ip, server_user, server_passwd)
        self.__satellite_subscribe(server_ip, server_user, server_passwd)
        self.__add_satellite62_repo(compose, server_ip, server_user, server_passwd)
        self.__install_satellite(server_ip, server_user, server_passwd)
        self.__deploy_satellite62(server_ip, server_user, server_passwd)
        self.__import_manifest_satellite(server_ip, server_user, server_passwd)

    def install_rhevm(self, compose, server_ip=None, server_user=None, server_passwd=None):
        self.cm_install_wget(server_ip)
        self.__rhevm_subscribe(server_ip, server_user, server_passwd)
        self.__add_rhevm_repo(compose, server_ip, server_user, server_passwd)
        self.__install_rhevm(server_ip, server_user, server_passwd)
        self.__deploy_rhevm(server_ip, server_user, server_passwd)

    def install_rhevm36(self, compose, server_ip=None, server_user=None, server_passwd=None):
        self.cm_install_wget(server_ip)
        self.__rhevm_subscribe(server_ip, server_user, server_passwd)
        self.__add_rhevm36_repo(compose, server_ip, server_user, server_passwd)
        self.__install_rhevm(server_ip, server_user, server_passwd)
        self.__deploy_rhevm36(server_ip, server_user, server_passwd)

    def install_rhevm40(self, compose, server_ip=None, server_user=None, server_passwd=None):
        self.cm_install_wget(server_ip)
        self.__rhevm_subscribe(server_ip, server_user, server_passwd)
        self.__add_rhevm40_repo(compose, server_ip, server_user, server_passwd)
        self.__install_rhevm(server_ip, server_user, server_passwd)
        self.__deploy_rhevm40(server_ip, server_user, server_passwd)

    def __stop_iptables(self, server_ip=None, server_user=None, server_passwd=None):
        cmd = "service iptables stop"
        ret, output = self.runcmd(cmd, "service iptables stop", server_ip, server_user, server_passwd)
#         if ret == 0:
#             logger.info("Succeeded to run service iptables stop.")
#         else:
#             raise FailException("Test Failed - Failed to run service iptables stop.")
#         cmd = "chkconfig iptables off"
#         ret, output = self.runcmd(cmd, "chkconfig iptables off", server_ip, server_user, server_passwd)
#         if ret == 0:
#             logger.info("Succeeded to run chkconfig iptables off.")
#         else:
#             raise FailException("Test Failed - Failed to run chkconfig iptables off.")
#         cmd = "service iptables save"
#         ret, output = self.runcmd(cmd, "service iptables save", server_ip, server_user, server_passwd)
#         if ret == 0:
#             logger.info("Succeeded to run service iptables save.")
#         else:
#             raise FailException("Test Failed - Failed to run service iptables save.")

    def __set_selinux(self, server_ip=None, server_user=None, server_passwd=None):
        cmd = "setenforce 0"
        ret, output = self.runcmd(cmd, "setenforce 0", server_ip, server_user, server_passwd)
        logger.info("Succeeded to run setenforce 0.")
#         if ret == 0:
#             logger.info("Succeeded to run setenforce 0.")
#         else:
#             raise FailException("Test Failed - Failed to run setenforce 0.")
        cmd = "sed -i -e 's/SELINUX=.*/SELINUX=%s/g' /etc/sysconfig/selinux" % ("permissive")
        ret, output = self.runcmd(cmd, "set /etc/sysconfig/selinux", server_ip, server_user, server_passwd)
        if ret == 0:
            logger.info("Succeeded to set /etc/sysconfig/selinux.")
        else:
            raise FailException("Test Failed - Failed to set /etc/sysconfig/selinux.")

    def __set_hosts_file(self, server_ip=None, server_user=None, server_passwd=None):
        if server_ip != None and server_ip != "":
            cmd = "sed -i '/%s/d' /etc/hosts; echo '%s %s' >> /etc/hosts" % (server_ip, server_ip, "samserv.redhat.com")
            ret, output = self.runcmd(cmd, "set /etc/hosts", server_ip, server_user, server_passwd)
            if ret == 0:
                logger.info("Succeeded to set /etc/hosts file.")
            else:
                raise FailException("Test Failed - Failed to set /etc/hosts file.")

    def __auto_subscribe(self, server_ip=None, server_user=None, server_passwd=None):
#         too slow for local install, add rhel repo instead
        cmd = "subscription-manager register --username=qa@redhat.com --password=a85xH8a5w8EaZbdS --auto-attach"
        ret, output = self.runcmd(cmd, "auto attach", server_ip, server_user, server_passwd)
        if ret == 0:
            logger.info("Succeeded to auto attach.")
        else:
            raise FailException("Test Failed - Failed to auto attach.")
#         cmd = ('cat <<EOF > /etc/yum.repos.d/myrhel.repo\n'
#             '[rhel]\n'
#             'name=rhel\n'
#             'baseurl=http://download.englab.nay.redhat.com/pub/rhel/released/RHEL-6/6.6/Server/x86_64/os/\n'
#             'enabled=1\n'
#             'gpgcheck=0\n'
#             '[rhel-optional]\n'
#             'name=rhel-optional\n'
#             'baseurl=http://download.englab.nay.redhat.com/pub/rhel/released/RHEL-6/6.6/Server/optional/x86_64/os/\n'
#             'enabled=1\n'
#             'gpgcheck=0\n'
#             'EOF'
#             )
#         self.runcmd(cmd)

    def __enable_sam_repo(self, server_ip=None, server_user=None, server_passwd=None):
        cmd = "yum-config-manager --disable; yum-config-manager --enable rhel-6-server-sam-rpms rhel-6-server-rpms"
        ret, output = self.runcmd(cmd, "enable sam repo", server_ip, server_user, server_passwd)
        if ret == 0:
            logger.info("Succeeded to enable sam repo")
        else:
            raise FailException("Test Failed - Failed to enable sam repo")

    def __satellite_subscribe(self, server_ip=None, server_user=None, server_passwd=None):
        cmd = "subscription-manager register --username=rhn-engineering-automation --password=KoKMAtikw1ifEPSe"
        ret, output = self.runcmd(cmd, "register system with ENG creds", server_ip, server_user, server_passwd)
        if ret == 0:
            logger.info("Succeeded to register system with ENG creds.")
        else:
            raise FailException("Test Failed - Failed to register system with ENG creds.")
        # cmd = "subscription-manager attach --pool=8a85f9823e3d5e43013e3e0af77e0f36"
        cmd = "subscription-manager attach --auto"
        ret, output = self.runcmd(cmd, "attach rhscl product", server_ip, server_user, server_passwd)
        if ret == 0:
            logger.info("Succeeded to attach rhscl product.")
        else:
            raise FailException("Test Failed - Failed to attach rhscl product.")
        cmd = "subscription-manager repos --disable \"*\""
        ret, output = self.runcmd(cmd, "disable all repo", server_ip, server_user, server_passwd)
        if ret == 0:
            logger.info("Succeeded to disable all repo.")
        else:
            raise FailException("Test Failed - Failed to disable all repo.")
        cmd = "subscription-manager repos --enable rhel-7-server-rpms --enable rhel-server-rhscl-7-rpms"
        ret, output = self.runcmd(cmd, "enable rhscl repo", server_ip, server_user, server_passwd)
        if ret == 0:
            logger.info("Succeeded to enable rhscl repo.")
        else:
            raise FailException("Test Failed - Failed to enable rhscl repo.")

    def __satellite62_subscribe(self, server_ip=None, server_user=None, server_passwd=None):
        cmd = "subscription-manager register --username=rhn-engineering-automation --password=KoKMAtikw1ifEPSe"
        ret, output = self.runcmd(cmd, "register system with ENG creds", server_ip, server_user, server_passwd)
        if ret == 0:
            logger.info("Succeeded to register system with ENG creds.")
        else:
            raise FailException("Test Failed - Failed to register system with ENG creds.")
        # cmd = "subscription-manager attach --pool=8a85f9823e3d5e43013e3e0af77e0f36"
        cmd = "subscription-manager attach --auto"
        ret, output = self.runcmd(cmd, "attach rhscl product", server_ip, server_user, server_passwd)
        if ret == 0:
            logger.info("Succeeded to attach rhscl product.")
        else:
            raise FailException("Test Failed - Failed to attach rhscl product.")
        cmd = "subscription-manager repos --disable \"*\""
        ret, output = self.runcmd(cmd, "disable all repo", server_ip, server_user, server_passwd)
        if ret == 0:
            logger.info("Succeeded to disable all repo.")
        else:
            raise FailException("Test Failed - Failed to disable all repo.")
        cmd = "subscription-manager repos --enable rhel-6-server-rpms --enable=rhel-6-server-optional-rpms --enable rhel-server-rhscl-6-rpms"
        ret, output = self.runcmd(cmd, "enable rhscl repo", server_ip, server_user, server_passwd)
        if ret == 0:
            logger.info("Succeeded to enable rhscl repo.")
        else:
            raise FailException("Test Failed - Failed to enable rhscl repo.")

    def __add_sam_repo(self, sam_compose, server_ip=None, server_user=None, server_passwd=None):
        # http://download.devel.redhat.com/devel/candidate-trees/SAM/%s/compose/SAM/x86_64/os/
        cmd = ('cat <<EOF > /etc/yum.repos.d/sam.repo\n'
            '[sam]\n'
            'name=sam\n'
            'baseurl=http://download.eng.bos.redhat.com/released/RHEL-6-SAM/x86_64/os/\n'
            'enabled=1\n'
            'gpgcheck=0\n'
            'EOF' % sam_compose
            )
        ret, output = self.runcmd(cmd, "add sam repo", server_ip, server_user, server_passwd)
        if ret == 0:
            logger.info("Succeeded to add sam repo.")
        else:
            raise FailException("Test Failed - Failed to add sam repo.")

    def __add_satellite_repo(self, satellite_compose, server_ip=None, server_user=None, server_passwd=None):
        cmd = ('cat <<EOF > /etc/yum.repos.d/satellite.repo\n'
            '[sat6]\n'
            'name=sat6\n'
            'baseurl=http://satellite6.lab.eng.rdu2.redhat.com/devel/candidate-trees/Satellite/%s/compose/Satellite/x86_64/os/\n'
            'enabled=1\n'
            'gpgcheck=0\n'
             
            '[sat6-capsule]\n'
            'name=Satellite 6 Capsule Packages\n'
            'baseurl=http://satellite6.lab.eng.rdu2.redhat.com/devel/candidate-trees/Satellite/%s/compose/Capsule/x86_64/os/\n'
            'enabled=1\n'
            'gpgcheck=0\n'
             
            '[sat6-rhcommon]\n'
            'name=Satellite 6 RH Common Packages\n'
            'baseurl=http://satellite6.lab.eng.rdu2.redhat.com/devel/candidate-trees/Satellite/%s/compose/sattools/x86_64/os/\n'
            'enabled=1\n'
            'gpgcheck=0\n'
            'EOF' % (satellite_compose, satellite_compose, satellite_compose)
            )
#         cmd = ('cat <<EOF > /etc/yum.repos.d/satellite.repo\n'
#             '[sat6]\n'
#             'name=sat6\n'
#             'baseurl=http://satellite6.lab.eng.rdu2.redhat.com/composes/%s/compose/Satellite/x86_64/os/\n'
#             'enabled=1\n'
#             'gpgcheck=0\n'
#             
#             '[sat6-capsule]\n'
#             'name=Satellite 6 Capsule Packages\n'
#             'baseurl=http://satellite6.lab.eng.rdu2.redhat.com/composes/%s/compose/Capsule/x86_64/os/\n'
#             'enabled=1\n'
#             'gpgcheck=0\n'
#             
#             '[sat6-rhcommon]\n'
#             'name=Satellite 6 RH Common Packages\n'
#             'baseurl=http://satellite6.lab.eng.rdu2.redhat.com/composes/%s/compose/sattools/x86_64/os/\n'
#             'enabled=1\n'
#             'gpgcheck=0\n'
#             'EOF' % (satellite_compose, satellite_compose, satellite_compose)
#             )
        ret, output = self.runcmd(cmd, "add satellite repo", server_ip, server_user, server_passwd)
        if ret == 0:
            logger.info("Succeeded to add satellite repo.")
        else:
            raise FailException("Test Failed - Failed to add satellite repo.")

    def __add_satellite62_repo(self, satellite_compose, server_ip=None, server_user=None, server_passwd=None):
        cmd = ('cat <<EOF > /etc/yum.repos.d/satellite.repo\n'
            '[sat6]\n'
            'name=sat6\n'
            'baseurl=http://satellite6.lab.eng.rdu2.redhat.com/composes/%s/compose/Satellite/x86_64/os/\n'
            'enabled=1\n'
            'gpgcheck=0\n'
              
            '[sat6-capsule]\n'
            'name=Satellite 6 Capsule Packages\n'
            'baseurl=http://satellite6.lab.eng.rdu2.redhat.com/composes/%s/compose/Capsule/x86_64/os/\n'
            'enabled=1\n'
            'gpgcheck=0\n'
              
            '[sat6-rhcommon]\n'
            'name=Satellite 6 RH Common Packages\n'
            'baseurl=http://satellite6.lab.eng.rdu2.redhat.com/composes/%s/compose/sattools/x86_64/os/\n'
            'enabled=1\n'
            'gpgcheck=0\n'
            'EOF' % (satellite_compose, satellite_compose, satellite_compose)
            )
#         cmd = ('cat <<EOF > /etc/yum.repos.d/satellite.repo\n'
#             '[sat6]\n'
#             'name=Satellite 6\n'
#             'baseurl=http://sat-perf-02.sat6.lab.eng.bos.redhat.com/pulp/repos/Sat6-CI/QA/Satellite_RHEL6/custom/Red_Hat_Satellite_6_2_Composes/RHEL6_Satellite_x86_64_os/\n'
#             'enabled=1\n'
#             'gpgcheck=0\n'
#             
#             '[sat6-capsule]\n'
#             'name=Satellite 6 Capsule Packages\n'
#             'baseurl=http://sat-perf-02.sat6.lab.eng.bos.redhat.com/pulp/repos/Sat6-CI/QA/Capsule_RHEL6/custom/Red_Hat_Capsule_6_2_Composes/RHEL6_Capsule_x86_64_os/\n'
#             'enabled=1\n'
#             'gpgcheck=0\n'
#             
#             '[sat6-tools]\n'
#             'name=Satellite 6 Tools Packages\n'
#             'baseurl=http://sat-perf-02.sat6.lab.eng.bos.redhat.com/pulp/repos/Sat6-CI/Library/Tools_RHEL6/custom/Red_Hat_Satellite_Tools_6_2_Composes/RHEL6_Satellite_Tools_x86_64_os/\n'
#             'enabled=1\n'
#             'gpgcheck=0'
#             'EOF'
#             )
        ret, output = self.runcmd(cmd, "add satellite repo", server_ip, server_user, server_passwd)
        if ret == 0:
            logger.info("Succeeded to add satellite repo.")
        else:
            raise FailException("Test Failed - Failed to add satellite repo.")

    def __install_katello(self, server_ip=None, server_user=None, server_passwd=None):
        cmd = "yum install -y katello-headpin-all"
        ret, output = self.runcmd(cmd, "yum install -y katello-headpin-all", server_ip, server_user, server_passwd, timeout=3600)
        # here it always time out, need to research reason
        if ret == 0:
            logger.info("Succeeded to run yum install -y katello-headpin-all.")
        else:
            raise FailException("Test Failed - Failed to run yum install -y katello-headpin-all.")

    def __deploy_sam(self, server_ip=None, server_user=None, server_passwd=None):
        cmd = "katello-configure --deployment=sam --user-pass=admin"
        ret, output = self.runcmd(cmd, "katello-configure", server_ip, server_user, server_passwd, timeout=1800)
        if ret == 0:
            logger.info("Succeeded to run katello-configure --deployment=sam --user-pass=admin.")
        else:
            raise FailException("Test Failed - Failed to run katello-configure --deployment=sam --user-pass=admin.")

    def __install_satellite(self, server_ip=None, server_user=None, server_passwd=None):
        cmd = "yum install -y katello"
        ret, output = self.runcmd(cmd, "yum install -y katello", server_ip, server_user, server_passwd, timeout=3600)
        if ret == 0:
            logger.info("Succeeded to run yum install -y katello.")
        else:
            raise FailException("Test Failed - Failed to run yum install -y katello.")

    def __deploy_satellite(self, server_ip=None, server_user=None, server_passwd=None):
        cmd = "katello-installer --foreman-admin-password=admin"
#         cmd = "foreman-installer --scenario katello --foreman-admin-password=admin"
        ret, output = self.runcmd(cmd, "katello-installer", server_ip, server_user, server_passwd, timeout=1800)
#         if ret == 0:
#             logger.info("Succeeded to run katello-installer --foreman-admin-password=admin.")
#         else:
#             raise FailException("Test Failed - Failed to run katello-installer --foreman-admin-password=admin.")

    def __deploy_satellite62(self, server_ip=None, server_user=None, server_passwd=None):
        cmd = "foreman-installer --scenario katello --foreman-admin-password=admin"
        ret, output = self.runcmd(cmd, "katello-installer", server_ip, server_user, server_passwd, timeout=1800)

    def __import_manifest(self, server_ip=None, server_user=None, server_passwd=None):
        # only support remote run
        self.__upload_manifest(server_ip, server_user, server_passwd)
        cmd = "headpin -u admin -p admin provider import_manifest --org=ACME_Corporation --name='Red Hat' --file=/root/sam_install_manifest.zip"
        ret, output = self.runcmd(cmd, "import menifest", server_ip, server_user, server_passwd)
        if ret == 0:
            logger.info("Succeeded to import menifest.")
        else:
            raise FailException("Test Failed - Failed to import menifest.")

    def __import_manifest_satellite(self, server_ip=None, server_user=None, server_passwd=None):
        # only support remote run
        self.__upload_manifest(server_ip, server_user, server_passwd)
        cmd = "hammer subscription upload --organization-label Default_Organization --file /root/sam_install_manifest.zip"
        ret, output = self.runcmd_interact(cmd, "hammer manifest upload", server_ip, server_user, server_passwd)
        if ret == 0:
            logger.info("Succeeded to import menifest.")
        else:
            raise FailException("Test Failed - Failed to import menifest.")

    def __upload_manifest(self, server_ip=None, server_user=None, server_passwd=None):
        # self.remote_put(sam_manifest, "/root/%s" % manifest_name)
        cmd = "wget %s/sam_install_manifest.zip -P /root/" % self.get_vw_cons("data_folder")
        ret, output = self.runcmd(cmd, "wget manifest to /root/", server_ip, server_user, server_passwd)
        if ret == 0:
            logger.info("Succeeded to wget manifest to /root/.")
        else:
            raise FailException("Test Failed - Failed to wget manifest to /root/.")

    def __add_rhevm_repo(self, rhevm_compose, server_ip=None, server_user=None, server_passwd=None):
        cmd = ('cat <<EOF > /etc/yum.repos.d/rhevm355.repo\n'
            '[rhevm355]\n'
            'name=rhevm355\n'
#             'baseurl=http://satellite6.lab.eng.rdu2.redhat.com/devel/candidate-trees/Satellite/%s/compose/Satellite/x86_64/os/\n'
            'baseurl=http://bob.eng.lab.tlv.redhat.com/builds/latest_vt/el%s/\n'
            'enabled=1\n'
            'gpgcheck=0\n'
            
            '[JBoss_latest]\n'
            'name=JBoss_latest\n'
            'baseurl=http://download.eng.pnq.redhat.com/released/JBEAP-6/6.4.4/composes/JBEAP-6.4.4-RHEL-%s/Server/x86_64/os/\n'
            'enabled=1\n'
            'gpgcheck=0\n'
            
            '[rhevm-mgent]\n'
            'name=rhevm-mgent\n'
            'baseurl=http://download.eng.bos.redhat.com/rel-eng/RHEV/3.5.1/latest/mgmt-agents/x86_64/os/\n'
            'enabled=1\n'
            'gpgcheck=0\n'
            
            '[RHEL_6.7_optional]\n'
            'name=RHEL_6.7_optional\n'
            'baseurl=http://download.eng.tlv.redhat.com/released/RHEL-6-Supplementary/6.7/Server/x86_64/os/\n'
            'enabled=1\n'
            'gpgcheck=0\n'
            'EOF' % (rhevm_compose, rhevm_compose)
            )
        ret, output = self.runcmd(cmd, "add rhevm repo", server_ip, server_user, server_passwd)
        if ret == 0:
            logger.info("Succeeded to add rhevm repo.")
        else:
            raise FailException("Test Failed - Failed to add rhevm repo.")

    def __add_rhevm36_repo(self, rhevm_compose, server_ip=None, server_user=None, server_passwd=None):
        cmd = ('cat <<EOF > /etc/yum.repos.d/rhevm36.repo\n'
            '[rhevm36]\n'
            'name=rhevm36\n'
#             'baseurl=http://satellite6.lab.eng.rdu2.redhat.com/devel/candidate-trees/Satellite/%s/compose/Satellite/x86_64/os/\n'
            'baseurl=http://bob.eng.lab.tlv.redhat.com/builds/latest_3.6/el%s/\n'
            'enabled=1\n'
            'gpgcheck=0\n'
            
            '[JBoss_latest]\n'
            'name=JBoss_latest\n'
            'baseurl=http://download.eng.tlv.redhat.com/pub/rhel/devel/candidates/JBEAP/composing/latest-JBEAP-6.4-RHEL-%s/compose/Server/x86_64/os/\n'
            'enabled=1\n'
            'gpgcheck=0\n'
            
            '[rhevm-mgent]\n'
            'name=rhevm-mgent\n'
            'baseurl=http://download.eng.bos.redhat.com/rel-eng/RHEV/3.5.1/latest/mgmt-agents/x86_64/os/\n'
            'enabled=1\n'
            'gpgcheck=0\n'
            
            '[RHEL_6.7_optional]\n'
            'name=RHEL_6.7_optional\n'
            'baseurl=http://download.eng.tlv.redhat.com/released/RHEL-6-Supplementary/6.7/Server/x86_64/os/\n'
            'enabled=1\n'
            'gpgcheck=0\n'
            'EOF' % (rhevm_compose, rhevm_compose)
            )
        ret, output = self.runcmd(cmd, "add rhevm repo", server_ip, server_user, server_passwd)
        if ret == 0:
            logger.info("Succeeded to add rhevm repo.")
        else:
            raise FailException("Test Failed - Failed to add rhevm repo.")

    def __add_rhevm40_repo(self, rhevm_compose, server_ip=None, server_user=None, server_passwd=None):
        cmd = "rpm -qa | grep rhev-release"
        ret, output = self.runcmd(cmd, "check rhev-latest package status", server_ip, server_user, server_passwd)
        if "rhev-release" in output:
            logger.info("Succeeded to check rhev-latest package exist.")
        else:
            logger.info("rhev-latest package is not install, need to install.")
            cmd = "rpm -Uvh http://bob.eng.lab.tlv.redhat.com/builds/latest_4.0/rhev-release-latest-4.0.noarch.rpm"
            ret, output = self.runcmd(cmd, "install rhev-latest package", server_ip, server_user, server_passwd)
            if ret == 0:
                logger.info("Succeeded to install rhev-latest package.")
            else:
                raise FailException("Test Failed - Failed to install rhev-latest package.")
        cmd = ('cat <<EOF > /etc/yum.repos.d/rhevm40.repo\n'
            '[rhevm40]\n'
            'name=rhevm40\n'
#             'baseurl=http://satellite6.lab.eng.rdu2.redhat.com/devel/candidate-trees/Satellite/%s/compose/Satellite/x86_64/os/\n'
            'baseurl=http://bob.eng.lab.tlv.redhat.com/builds/latest_4.0/el%s/\n'
            'enabled=1\n'
            'gpgcheck=0\n'
            
            '[test_rhel_z_stream]\n'
            'name=RHEL_7.2_candidate_zstream\n'
            'baseurl=http://download.eng.tlv.redhat.com/rel-eng/repos/rhel-7.2-z-candidate/x86_64/\n'
            'enabled=1\n'
            'gpgcheck=0\n'
            
            '[rhev-72-hypervisor]\n'
            'name=rhev-72-hypervisor\n'
            'baseurl=http://download.eng.tlv.redhat.com/rel-eng/repos/rhevh-rhel-7.2-candidate/x86_64/\n'
            'enabled=1\n'
            'gpgcheck=0\n'
            'EOF' % (rhevm_compose, rhevm_compose)
            )
        ret, output = self.runcmd(cmd, "add rhevm repo", server_ip, server_user, server_passwd)
        if ret == 0:
            logger.info("Succeeded to add rhevm repo.")
        else:
            raise FailException("Test Failed - Failed to add rhevm repo.")

    def __install_rhevm(self, server_ip=None, server_user=None, server_passwd=None):
        cmd = "yum install -y rhevm"
        ret, output = self.runcmd(cmd, "yum install -y rhevm", server_ip, server_user, server_passwd, timeout=36000)
        if ret == 0:
            logger.info("Succeeded to run yum install -y rhevm.")
        else:
            raise FailException("Test Failed - Failed to run yum install -y rhevm.")

    def __deploy_rhevm(self, server_ip=None, server_user=None, server_passwd=None):
        ''' wget rhevm config file to rhevm '''
        cmd = "wget -P /root/ %s/rhevm355_config" % self.get_vw_cons("data_folder")
        ret, output = self.runcmd(cmd, "wget rhevm repo file and add to rhel host", server_ip, server_user, server_passwd)
        if ret == 0:
            logger.info("Succeeded to wget rhevm config file to rhevm")
        else:
            raise FailException("Failed to wget rhevm config file to rhevm")
        rhevm_hostname = self.get_hostname(server_ip)
        cmd = "sed -i -e 's/rhevmhostname/%s/g' /root/rhevm355_config" % rhevm_hostname
        ret, output = self.runcmd(cmd, "updating repo file to the latest rhel repo", server_ip, server_user, server_passwd)
        if ret == 0:
            logger.info("Succeeded to update repo file to the latest rhel repo")
        else:
            raise FailException("Test Failed - Failed to update repo file to the latest rhel repo")

        cmd = "rhevm-setup --config-append=/root/rhevm355_config"
        ret, output = self.runcmd(cmd, "rhevm-configure", server_ip, server_user, server_passwd, timeout=1800)
        if ret == 0:
            logger.info("Succeeded to run rhevm-configure --deployment=sam --user-pass=admin.")
        else:
            raise FailException("Test Failed - Failed to run rhevm-configure --deployment=sam --user-pass=admin.")

    def __deploy_rhevm36(self, server_ip=None, server_user=None, server_passwd=None):
        ''' wget rhevm config file to rhevm '''
        cmd = "wget -P /root/ %s/rhevm36_config" % self.get_vw_cons("data_folder")
        ret, output = self.runcmd(cmd, "wget rhevm repo file and add to rhel host", server_ip, server_user, server_passwd)
        if ret == 0:
            logger.info("Succeeded to wget rhevm config file to rhevm")
        else:
            raise FailException("Failed to wget rhevm config file to rhevm")
        rhevm_hostname = self.get_hostname(server_ip)
        cmd = "sed -i -e 's/rhevmhostname/%s/g' /root/rhevm36_config" % rhevm_hostname
        ret, output = self.runcmd(cmd, "updating repo file to the latest rhel repo", server_ip, server_user, server_passwd)
        if ret == 0:
            logger.info("Succeeded to update repo file to the latest rhel repo")
        else:
            raise FailException("Test Failed - Failed to update repo file to the latest rhel repo")

        cmd = "engine-setup --config-append=/root/rhevm36_config"
        ret, output = self.runcmd(cmd, "rhevm-configure", server_ip, server_user, server_passwd, timeout=1800)
        if ret == 0:
            logger.info("Succeeded to run rhevm-configure --deployment=sam --user-pass=admin.")
        else:
            raise FailException("Test Failed - Failed to run rhevm-configure --deployment=sam --user-pass=admin.")

    def __deploy_rhevm40(self, server_ip=None, server_user=None, server_passwd=None):
        ''' wget rhevm config file to rhevm '''
        cmd = "wget -P /root/ %s/rhevm_40_2_config" % self.get_vw_cons("data_folder")
        ret, output = self.runcmd(cmd, "wget rhevm repo file and add to rhel host", server_ip, server_user, server_passwd)
        if ret == 0:
            logger.info("Succeeded to wget rhevm config file to rhevm")
        else:
            raise FailException("Failed to wget rhevm config file to rhevm")
        rhevm_hostname = self.get_hostname(server_ip)
        cmd = "sed -i -e 's/rhevmhostname/%s/g' /root/rhevm40_config" % rhevm_hostname
        ret, output = self.runcmd(cmd, "updating repo file to the latest rhel repo", server_ip, server_user, server_passwd)
        if ret == 0:
            logger.info("Succeeded to update repo file to the latest rhel repo")
        else:
            raise FailException("Test Failed - Failed to update repo file to the latest rhel repo")

        cmd = "engine-setup --config-append=/root/rhevm40_config"
        ret, output = self.runcmd(cmd, "rhevm-configure", server_ip, server_user, server_passwd, timeout=1800)
        if ret == 0:
            logger.info("Succeeded to run rhevm-configure --deployment=sam --user-pass=admin.")
        else:
            raise FailException("Test Failed - Failed to run rhevm-configure --deployment=sam --user-pass=admin.")

    def __rhevm_subscribe(self, server_ip=None, server_user=None, server_passwd=None):
        cmd = "subscription-manager register --username=rhn-engineering-automation --password=KoKMAtikw1ifEPSe"
        ret, output = self.runcmd(cmd, "register system with ENG creds", server_ip, server_user, server_passwd)
        if ret == 0:
            logger.info("Succeeded to register system with ENG creds.")
        else:
            raise FailException("Test Failed - Failed to register system with ENG creds.")
        cmd = "subscription-manager attach --auto"
        ret, output = self.runcmd(cmd, "attach rhscl product", server_ip, server_user, server_passwd)
        if ret == 0:
            logger.info("Succeeded to attach rhscl product.")
        else:
            raise FailException("Test Failed - Failed to attach rhscl product.")
