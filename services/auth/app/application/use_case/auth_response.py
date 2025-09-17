class AuthResponse:
    def __init__(self, user=None, tokens=None, error=None, status_code=200):
        self.user = user
        self.tokens = tokens
        self.error = error
        self.status_code = status_code

    def to_dict(self):
        if self.error:
            return {
                "error": self.error
            }

        return {
            "user": self.user,
            "tokens": self.tokens
        }
