from utils import *
from testcases.rhsm.rhsm_gui.rhsmguibase import RHSMGuiBase
from testcases.rhsm.rhsm_gui.rhsmguilocator import RHSMGuiLocator
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID178195_GUI_reregister_when_registered(RHSMGuiBase):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % self.__class__.__name__)
        try:
            try:
                username = RHSMConstants().get_constant("username")
                password = RHSMConstants().get_constant("password")
                self.open_subscription_manager()
                self.check_consumer_cert_files(exist=False)
                self.click_register_button()
                self.click_dialog_next_button()
                self.input_username(username)
                self.input_password(password)
                self.check_manual_attach_checkbox()
                self.click_dialog_register_button_without_autoattach()
                self.check_consumer_cert_files(exist=True)
                if self.check_object_status("main-window", "register-menu", "VISIBLE") == 0:
                    logger.info("It's successful to check register-menu is not visible")
                else:
                    raise FailException("Test Faild - Failed to check register-menu is not visible")
                if self.check_object_status("main-window", "unregister-menu", "VISIBLE") == 1:
                    logger.info("It's successful to check unregister-menu is visible")
                else:
                    raise FailException("Test Faild - Failed to check unregister-menu is visible")
                self.assert_(True, case_name)
            except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                self.assert_(False, case_name)
        finally:
            self.capture_image(case_name)
            self.restore_gui_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()