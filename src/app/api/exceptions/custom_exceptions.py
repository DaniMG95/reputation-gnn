class AppBaseException(Exception):
    def __init__(self, message: str, status_code: int = 400, code: str = "BAD_REQUEST"):
        self.message = message
        self.status_code = status_code
        self.code = code
        super().__init__(self.message)

class PersonNotFoundError(AppBaseException):
    def __init__(self, name: str):
        super().__init__(message=f"Person with name '{name}' not found.", status_code=404, code="PERSON_NOT_FOUND")

class GNNModelNotLoaded(AppBaseException):
    def __init__(self):
        super().__init__(status_code=500, code="GNN_MODEL_NOT_LOADED",
                         message="The GNN model has not been loaded. Please load the model before making predictions.")

class GNNModelPredictionError(AppBaseException):
    def __init__(self):
        super().__init__(status_code=500, code="GNN_MODEL_PREDICTION_ERROR",
                         message="An error occurred during GNN model prediction. Please check the input data "
                                 "and try again.")

class PersonAlreadyExistsError(AppBaseException):
    def __init__(self, name: str):
        super().__init__(message=f"Person with name '{name}' already exists.", status_code=400,
                         code="PERSON_ALREADY_EXISTS")

class InvalidPaginationParametersError(AppBaseException):
    def __init__(self, message: str):
        super().__init__(message=message, status_code=400, code="INVALID_PAGINATION_PARAMETERS")

class InvalidModelError(AppBaseException):
    def __init__(self, message: str):
        super().__init__(message=message, status_code=400, code="INVALID_MODEL")
