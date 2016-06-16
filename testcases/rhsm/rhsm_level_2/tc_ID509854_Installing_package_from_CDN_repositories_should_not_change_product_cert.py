from utils import *
from testcases.rhsm.rhsmbase import RHSMBase
from utils.exception.failexception import FailException

class tc_ID509854_Installing_package_from_CDN_repositories_should_not_change_product_cert(RHSMBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            username = self.get_rhsm_cons("username")
            password = self.get_rhsm_cons("password")
            self.sub_register(username, password)
            autosubprod = self.get_rhsm_cons("autosubprod")
            self.sub_autosubscribe(autosubprod)

            # Save product cert info
            self.save_product_cert_info('/root/p1')

            # Insall a pakage
            pkgtoinstall = self.get_rhsm_cons('pkgtoinstall')
            self.install_pkg(pkgtoinstall)

            # Save product cert info again
            self.save_product_cert_info('/root/p2')

            # Compare product certs
            cmd = "diff /root/p1 /root/p2"
            (ret, output) = self.runcmd(cmd, "compare products certs")
            if ret ==0 and ''==output:
                logger.info("It's successful to compare products certs")
            else:
                raise FailException("Test Failed - Failed to compare products certs")
            
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            self.remove_pkg(pkgtoinstall)
            self.restore_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

    def save_product_cert_info(self, savepath):
        cmd = "rct cat-cert /etc/pki/product-default/69.pem  > %s"%savepath
        (ret, output) = self.runcmd(cmd, "Save product cert info")
        if ret ==0:
            logger.info("It's successful to save product cert info to %s"%savepath)
        else:
            raise FailException("Test Failed - Failed to save product cert info to %s"%savepath)

if __name__ == "__main__":
    unittest.main()
