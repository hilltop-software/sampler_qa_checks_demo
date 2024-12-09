from typing import List
from HilltopHost.Sampler import QACheck

class ICheck:
    """
    Interface for all checks. Each check performs validation logic and returns a list of CheckResult objects.
    """
    
    def __init__(self, config):
        self.config = config
        
    def perform_checks(self, context) -> List[QACheck]:
        raise NotImplementedError("Must implement perform_check method.")