class ILocatorHealer:
    def heal(self, *, page, exception):
        """
        Returns a new Playwright Locator
        """
        raise NotImplementedError
