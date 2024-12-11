# src/pytestifypro/ui/pages/login_page_locators.py

from selenium.webdriver.common.by import By

class LoginPageLocators:
    SSO_LOGIN_BUTTON = (By.XPATH, "//button[contains(text(), 'Log in with Azure')]")
    #USERNAME_FIELD = (By.NAME, "loginfmt")
    USERNAME_FIELD = (By.ID, "i0116")
    NEXT_BUTTON = (By.ID, "idSIButton9")
    #PASSWORD_FIELD = (By.NAME, "passwd")
    PASSWORD_FIELD = (By.ID, "i0118")
    SIGN_IN_BUTTON = (By.ID, "idSIButton9")
    STAY_SIGNED_IN_BUTTON = (By.ID, "idSIButton9")

