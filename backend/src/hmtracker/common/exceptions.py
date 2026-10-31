class HMTrackerError(Exception):
    """Base exception for HMTracker"""


class HMAuthenticationError(HMTrackerError):
    """Hockey Manager credentials could not be authenticated."""

    def __init__(self):
        super().__init__("Incorrect Hockey Manager username or password")


class HMUnavailableError(HMTrackerError):
    """Hockey Manager could not complete the login request."""

    def __init__(self):
        super().__init__(
            "Hockey Manager is temporarily unavailable. Please try again later."
        )


class NoEncryptionError(HMTrackerError):
    """No private key set for encryption"""


class NoDatabaseError(HMTrackerError):
    """No database set in backend"""
