# Initial setup

## Prerequisites
You will need:
1. A [Groundlight account](https://dashboard.groundlight.ai/)
2. An API token from the [Groundlight dashboard](https://dashboard.groundlight.ai/reef/my-account/api-tokens)
3. Python 3.9+


## Install the Groundlight SDK
Groundlight provides a Python (3.9+) SDK that you can use to interact with the Groundlight API.

In your project directory, create a virtual environment.
```bash
python -m venv groundlight-env
```

Activate the virtual environment using
- On macOS or Linux, `source groundlight-env/bin/activate`
- On Windows, `.\groundlight-env\Scripts\activate`

Install the Groundlight SDK using pip:
```bash
pip install groundlight
```

## Set your API token
Every request to the Groundlight API requires an API token. The Groundlight SDK is designed to pull the API token from an environment variable `GROUNDLIGHT_API_TOKEN`.

Set the API token in your terminal:
```bash
# MacOS / Linux
export GROUNDLIGHT_API_TOKEN='your-api-token'
```
```powershell
# Windows
setx GROUNDLIGHT_API_TOKEN "your-api-token"
```

## Call the Groundlight API
Call the Groundlight API by creating a `Detector` and submitting an `ImageQuery`.

```python title="ask.py"
from groundlight import Groundlight, Detector, ImageQuery

gl = Groundlight()

det: Detector = gl.get_or_create_detector(name="parking-space", query="Is there a car in the leftmost parking space?")

img = "./docs/static/img/doorway.jpg"  # Image can be a file or a Python object
image_query = gl.submit_image_query(detector=det, image=img)
print(f"The answer is {image_query.result.label}")
print(image_query)
```

Run the code using `python3 ask.py`. The code will submit an image to the Groundlight API and print the result:
```
The answer is NO
ImageQuery(
    id='iq_2pL5wwlefaOnFNQx1X6awTOd119',
    query="Is there a car in the leftmost parking space?",
    detector_id='det_2owcsT7XCsfFlu7diAKgPKR4BXY',
    result=BinaryClassificationResult(
        confidence=0.9995857543478209,
        label=<Label.NO: 'NO'>
    ),
    created_at=datetime.datetime(2024, 11, 25, 11, 5, 57, 38627, tzinfo=tzutc()),
    patience_time=30.0,
    confidence_threshold=0.9,
    type=<ImageQueryTypeEnum.image_query: 'image_query'>,
    result_type=<ResultTypeEnum.binary_classification: 'binary_classification'>,
    metadata=None
)
```