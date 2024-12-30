class NoMoreRecipesError(Exception):
    """Exception raised when there are no more recipes to scrape."""
    def __init__(self, message="No more recipes available to scrape."):
        self.message = message
        super().__init__(self.message)