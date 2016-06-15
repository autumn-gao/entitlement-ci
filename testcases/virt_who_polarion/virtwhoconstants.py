class VIRTWHOConstants(object):
    virtwho_cons = {

    "data_server":                      "10.66.144.9",
    "data_folder":                      "https://github.com/bluesky-sgao/entitlement-ci/raw/master/data",

    "local_image_server":               "10.66.144.9:/data/projects/sam-virtwho/pub",
    "beaker_image_server":              "10.16.96.131:/home/samdata",

    # for kvm
    "KVM_GUEST_NAME":                   "6.7_Server_x86_64",
    "nfs_image_path":                   "/root/images_nfs",
    "local_mount_point":                "/tmp/images_mnt",

    # for esx
    "ESX_HOST":                         "10.66.128.10",
    "ESX_HOST_SECOND":                  "10.66.128.77",
    "ESX_GUEST_NAME":                   "ESX_7.1_Server_x86_64",
    "VMWARE_CMD_IP":                    "10.73.5.226",
    "VIRTWHO_ESX_SERVER":               "10.73.3.181",
    "VIRTWHO_ESX_USERNAME":             "administrator@vsphere.local",
    "VIRTWHO_ESX_PASSWORD":             "Welcome1!",

    # for rhevm
    "NFSserver_ip":                     "10.16.96.131",
    "proxy_ip":                         "proxy=https:\/\/squid.corp.redhat.com:3128",
    "RHEL_RHEVM_GUEST_NAME":            "6.7_Server_x86_64",
    "NFS_DIR_FOR_storage":              "/root/data",
    "NFS_DIR_FOR_export":               "/root/export",
    "VIRTWHO_RHEVM_USERNAME":           "admin@internal",
    "VIRTWHO_RHEVM_PASSWORD":           "redhat",
    "VIRTWHO_LIBVIRT_USERNAME":         "root",
    "VIRTWHO_LIBVIRT_PASSWORD":         "",

    # for hyperv
    "HYPERV_HOST":                          "10.73.5.212",
    "HYPERV_PORT":                          6555,
    "HYPERV_GUEST_NAME":                    "HYPERV_7.2_Server_x86_64",
    "VIRTWHO_HYPERV_SERVER":                "10.73.5.212",
    "VIRTWHO_HYPERV_USERNAME":              "administrator",
    "VIRTWHO_HYPERV_PASSWORD":              "Welcome1",

    # for xen
    "XEN_HOST":                             "10.73.5.210",
    "XEN_GUEST_NAME":                       "XEN_6.8_Server_x86_64",
    "VIRTWHO_XEN_SERVER":                   "10.73.5.210",
    "VIRTWHO_XEN_USERNAME":                 "root",
    "VIRTWHO_XEN_PASSWORD":                 "Welcome1",

    # limited subscription
    "productid_guest":                  "RH0103708",
    "productname_guest":                "Red Hat Enterprise Linux Server, Premium",
    "guestlimit":                       "4",
    # unlimited subscription
    "productid_unlimited_guest":        "RH00060",
    "productname_unlimited_guest":      "Resilient Storage for Unlimited Guests",
    "guestlimit_unlimited_guest":       "Unlimited",
    # Datacenter subscription
    "datacenter_name":                  "Red Hat Enterprise Linux for Virtual Datacenters, Standard",
    "datacenter_bonus_name":            "Red Hat Enterprise Linux for Virtual Datacenters, Standard (DERIVED SKU)",
    "datacenter_sku_id":                "RH00002",
    "datacenter_bonus_sku_id":          "RH00050",
    "datacenter_bonus_quantity":        "Unlimited",
    # Datacenter subscription
    "instancebase_name":                "Red Hat Enterprise Linux Server, Premium (Physical or Virtual Nodes)",
    "instancebase_sku_id":              "RH00003",

    # message constant, maybe create a new file in future
    "wrong_owner":                          "xxxxxxx",
    "wrong_env":                            "xxxxxxx",

    "esx_error_msg_without_owner":              "Option --esx-owner (or VIRTWHO_ESX_OWNER environment variable) needs to be set",
    "esx_error_msg_with_wrong_owner":           "Couldn't find organization 'xxxxxxx'",
    "esx_error_msg_without_owner_in_conf":      "Option `owner` needs to be set in config `esx`",
    "esx_error_msg_without_env":                "Option --esx-env (or VIRTWHO_ESX_ENV environment variable) needs to be set",
    "esx_error_msg_with_wrong_env":             "Couldn't find environment 'xxxxxxx'",
    "esx_error_msg_without_env_in_conf":        "Option `env` needs to be set in config `esx`",

    "hyperv_error_msg_without_owner":           "Option --hyperv-owner (or VIRTWHO_HYPERV_OWNER environment variable) needs to be set",
    "hyperv_error_msg_with_wrong_owner":        "Couldn't find organization 'xxxxxxx'",
    "hyperv_error_msg_without_owner_in_conf":   "Option `owner` needs to be set in config `hyperv`",
    "hyperv_error_msg_without_env":             "Option --hyperv-env (or VIRTWHO_HYPERV_ENV environment variable) needs to be set",
    "hyperv_error_msg_with_wrong_env":          "Couldn't find environment 'xxxxxxx'",
    "hyperv_error_msg_without_env_in_conf":     "Option `env` needs to be set in config `hyperv`",

    "xen_error_msg_without_owner":           "Option --xen-owner (or VIRTWHO_XEN_OWNER environment variable) needs to be set",
    "xen_error_msg_with_wrong_owner":        "Couldn't find organization 'xxxxxxx'",
    "xen_error_msg_without_owner_in_conf":   "Option `owner` needs to be set in config `xen`",
    "xen_error_msg_without_env":             "Option --xen-env (or VIRTWHO_XEN_ENV environment variable) needs to be set",
    "xen_error_msg_with_wrong_env":          "Couldn't find environment 'xxxxxxx'",
    "xen_error_msg_without_env_in_conf":     "Option `env` needs to be set in config `xen`",

    "rhevm_error_msg_without_owner":            "Option --rhevm-owner (or VIRTWHO_RHEVM_OWNER environment variable) needs to be set",
    "rhevm_error_msg_with_wrong_owner":         "Couldn't find organization 'xxxxxxx'",
    "rhevm_error_msg_without_owner_in_conf":    "Option `owner` needs to be set in config `rhevm`",
    "rhevm_error_msg_without_env":              "Option --rhevm-env (or VIRTWHO_RHEVM_ENV environment variable) needs to be set",
    "rhevm_error_msg_with_wrong_env":           "Couldn't find environment 'xxxxxxx'",
    "rhevm_error_msg_without_env_in_conf":      "Option `env` needs to be set in config `rhevm`",

    "libvirt_error_msg_without_owner":              "Option `owner` needs to be set in config `env/cmdline`",
    "libvirt_error_msg_with_wrong_owner":           "Couldn't find organization 'xxxxxxx'",
    "libvirt_error_msg_without_owner_in_conf":      "Option `owner` needs to be set in config `libvirt`",
    "libvirt_error_msg_without_env":                " Option `env` needs to be set in config `env/cmdline`",
    "libvirt_error_msg_with_wrong_env":             "Couldn't find environment 'xxxxxxx'",
    "libvirt_error_msg_without_env_in_conf":        "Option `env` needs to be set in config `libvirt`",

    }

    sam_cons = {
    "username":                         "admin",
    "password":                         "admin",
    "server_owner":                     "ACME_Corporation",
    "server_env":                       "Library",
    }

    satellite_cons = {
    "username":                         "admin",
    "password":                         "admin",
    "server_owner":                     "ACME_Corporation",
    "server_env":                       "Library",
    }

    stage_cons = {
    "username":                         "stage_virtwho_test_2016",
    "password":                         "redhat",
    "server_owner":                     "7715246",
    "server_env":                       "7715246",
    }

    virt_who_commands = {
    "restart_virtwho":                  "service virt-who restart",
    "restart_virtwho_systemd":          "systemctl restart virt-who.service",
    
    "stop_virtwho":                     "service virt-who stop",
    "stop_virtwho_systemd":             "systemctl stop virt-who.service",
    
    "status_virtwho":                   "service virt-who status",
    "status_virtwho_systemd":           "systemctl status virt-who.service",
    
    "restart_libvirtd":                 "service libvirtd restart",
    "restart_libvirtd_systemd":         "systemctl restart libvirtd.service",
    
    "restart_network":                  "service network restart",
    "restart_network_systemd":          "systemctl restart network",
    }

    virtwho_sam_cons = dict(virtwho_cons.items() + sam_cons.items())
    virtwho_satellite_cons = dict(virtwho_cons.items() + satellite_cons.items())
    virtwho_stage_cons = dict(virtwho_cons.items() + stage_cons.items())

    __instance = None
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(VIRTWHOConstants, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance
 
    def __init__(self):
        if(self.__initialized): return
        else: self.__initialized = True
