def forgotPasswordEmailTemplate(email: str, user_name: str, link: str) -> str:
    return f"""
        <html>
            <body>
                <div class="header" style="
                    width: 100%;
                    color: #0798f2;
                    font-weight: 700;
                    font-size: 2.5rem;
                    margin-bottom: 2rem;
                    padding-bottom: 0.5rem;
                    border-bottom: 2px solid #0798f2
                    ">
                    Personalize<span style="color: #f2bc1b">GPT</span>
                </div>

                Hi {user_name},<br><br>

                We've received a request to reset the password for your PersonalizeGPT accound associated with {email}. No changes have been made to your account yet. 
                You can reset your password by clicking the link below.<br><br>

                <a class="link" href="{link}" style="
                    background-color:  #0798f2; 
                    color: white; 
                    padding: 10px 15px; 
                    text-align: center; 
                    text-decoration: none; 
                    display: inline-block; 
                    border-radius: 5px;
                    font-weight: 700;
                    "
                    style:active="color: white;"
                    >Reset Your Password</a><br><br>

                <i>Please ignore this email if you did not request a password change.</i><br><br>
                
                From,<br>
                PersonalizeGPT.
            </body>
            </html>
        <html>
    """