class ValidationError(object):
    def __init__(self):
        self.summary_message = None
        self.inline_message = None
        self.explanatory_text = None
