class ResearchSafety:
    """Research integrity controls; this system does not execute trades."""
    def validate(self, lookahead=False, confirmed=True):
        return bool(not lookahead and confirmed)
