class HMTrackerError(Exception):
    """Base exception for HMTracker"""


class NoEncryptionError(HMTrackerError):
    """No private key set for encryption"""


class NoDatabaseError(HMTrackerError):
    """No database set in backend"""
