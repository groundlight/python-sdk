# flake8: noqa

# import all models into this package
# if you have many models here with many references from one model to another this may
# raise a RecursionError
# to avoid this, import only the models that you directly need like:
# from from openapi_client.model.pet import Pet
# or import this package, but before doing it, use:
# import sys
# sys.setrecursionlimit(n)

from openapi_client.model.classification_result import ClassificationResult
from openapi_client.model.detector import Detector
from openapi_client.model.detector_creation_input import DetectorCreationInput
from openapi_client.model.detector_type_enum import DetectorTypeEnum
from openapi_client.model.image_query import ImageQuery
from openapi_client.model.image_query_type_enum import ImageQueryTypeEnum
from openapi_client.model.paginated_detector_list import PaginatedDetectorList
from openapi_client.model.paginated_image_query_list import PaginatedImageQueryList
from openapi_client.model.result_type_enum import ResultTypeEnum
