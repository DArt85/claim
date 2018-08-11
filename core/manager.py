
from claim.handlers import *
from claim.common.utils import Singleton

class ModelManager(metaclass=Singleton):
    """
    Proxy class allowing model management and containing logic to select and 
    apply handling models to claims.
    """

    class ManagerException(Exception):
        def __init__(self, msg):
            super().__init__(msg)

    def __init__(self):
        self._models = []
        self._default_model = None

    def add_model(self, model):
        if not issubclass(model, AbstractClaimHandler):
            raise ManagerException("Model should be a subclass of %s" % AbstractClaimHandler)
        self._models.append(model)

    def set_default_model(self, model_cl):
        for mod in self._models:
            if isinstance(mod, model_cl):
                self._default_model = mod
                break

        if not self._default_model:
            raise ManagerException("Can't set model %s before it is added" % model_cl)

    def process_claims(self, claims):
        return [self._default_model.classify_claim(c) for c in claims]
