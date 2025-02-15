import os
from sendgrid import SendGridAPIClient
from uuid import uuid4
from sendgrid.helpers.mail import Mail
from services.user_service import UserService
from utils.email_utils import forgotPasswordEmailTemplate

class MailService:
    def __init__(self) -> None:
        self.user_service = UserService()
        self.RESET_KEY = 'reset_token'
        self.FROM_EMAIL = "personalizegpt@gmail.com"
        self.client = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))

    def send_reset_email(self, email: str):
        try:
            subject = "Reset your PersonalizeGPT password"
            reset_link, conf_token = self.generate_reset_link()
            user_profile = self.user_service.get_user_profile_by_email(email)

            if not user_profile._id:
                raise ValueError("User ID is missing or invalid")

            user_name = user_profile.first_name + " " + user_profile.last_name 
            self.user_service.update_a_specific_key(user_profile._id, self.RESET_KEY, conf_token)

            template = forgotPasswordEmailTemplate(email, user_name, reset_link)

            message = Mail(
                from_email=self.FROM_EMAIL,
                to_emails=email,
                subject=subject,
                html_content=template
            )

            self.client.send(message)

        except Exception as e:
            raise e


    def generate_reset_link(self):
        conf_token = str(uuid4())
        reset_url = f"{os.getenv('FRONTEND_URL')}/password-reset/{conf_token}"
        return reset_url, conf_token
