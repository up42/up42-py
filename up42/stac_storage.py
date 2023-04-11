from up42.auth import Auth
from up42.storage import Storage


class StacStorage :
    """
    The StacStorage class is used to search and interact with the STAC catalog in the UP42 workspace.
    """
    
    def __init__(self, auth: Auth):
        self.auth = auth
        self.storage = Storage(auth=self.auth)
        pass
    
    
    