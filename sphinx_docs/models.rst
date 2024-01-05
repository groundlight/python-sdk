SDK Client
=====================

.. autoclass:: groundlight.Groundlight 
   :members:
   :special-members: __init__


Groundlight Client
==================

.. automodule:: groundlight.client 
   :members:
   :special-members: __init__
   :exclude-members: ApiTokenError


API Response Objects
=====================

.. autopydantic_model:: model.Detector 
   :model-show-json: True 

.. autopydantic_model:: model.ImageQuery
   :model-show-json: True 

.. autopydantic_model:: model.PaginatedDetectorList
    :model-show-json: True 

.. autopydantic_model:: model.PaginatedImageQueryList
    :model-show-json: True 