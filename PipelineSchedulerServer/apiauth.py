__author__ = 'Christoph Jansen, HTW Berlin'

class TokenAuthenticator:
    def __init__(self, tokens):
        self.tokens = tokens

    def authorize(self, token):
        if not self.tokens:
            return True
        if not token:
            return False
        for t in self.tokens:
            if t == token:
                return True
        return False