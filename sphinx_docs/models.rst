SDK Client
=====================

.. autoclass:: groundlight.Groundlight
   :members:
   :special-members: __init__

.. autoclass:: groundlight.ExperimentalApi
   :members:
   :special-members: __init__

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

.. autopydantic_model:: model.Rule
    :model-show-json: True

.. autopydantic_model:: model.PaginatedRuleList
    :model-show-json: True