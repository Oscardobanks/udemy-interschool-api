from fastapi.security import OAuth2PasswordRequestForm 
from typing import List
from fastapi import Form

class OAuth2PasswordRequestFormWithRole(OAuth2PasswordRequestForm):
    def __init__(
        self, 
        username: str = Form(...), 
        password: str = Form(...), 
        # role: List[str] = ["Student", "Instructor"]
        role: str = Form(..., regex="^(student|instructor)$")
    ):
        super().__init__(username=username, password=password)
        self.role = role