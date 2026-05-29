from abc import ABC, abstractmethod

class FanControlBase(ABC):
    """Base interface for fan controllers."""
    
    @abstractmethod
    def start(self):
        """Starts the fan control."""
        pass
        
    @abstractmethod
    def stop(self):
        """Stops the fan control."""
        pass

    @abstractmethod
    def get_state(self):
        """Returns the current state of the fan control."""
        pass
