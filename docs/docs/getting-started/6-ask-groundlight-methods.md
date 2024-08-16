# Ask Groundlight Methods

The python-sdk provides a few different methods for submitting images to Groundlight depending on
your use case. All of these methods take an image and an identifier for the detector you want to
send the image to and return an `ImageQuery` object which contains the answer from Groundlight.
The different methods provide different ways to utilize Groundlight's escalation logic.

## `ask_ml`

`ask_ml` is the most direct method for submitting an image query and asks for the fastest available ML answer
from Groundlight. Groundlight's escalation logic will still run in order to improve the model's
confidence for future queries.

`ask_ml` is a good choice in most situations including live monitoring,

## `ask_confident`

`ask_confident` give you access to high quality and human reviewed answers from Groundlight. Rather
than get the first available answer, `ask_confident` will continue to wait as the image makes its
way through the escalation process until either a more powerful model can give a high confidence
answer or a human reviewer can provide a definitive answer. How confident the answer needs to be can
be configured through the `confidence_threshold` parameter.

This is
ideal in critical situations like quality control or safety monitoring where mistakes can be costly
and you can wait a little longer for a more accurate answer. You can also use `ask_confident` as a
filter after recieving an answer from `ask_ml` to provide a level of review before triggering any
operations or contingencies.

(You can program your own operations to be triggered by groundlight, but if you're interested in recieving text message or email notifications see if Groundlight alerts would meet your needs)

## `ask_async`

There are some cases where you may not need an answer from Groundlight right away, often when you're
submitting a batch of images. You may want to provide historical images you have in order to prepare
a detector for future use, or you may want to submit a set of images to multiple detectors
simultaneously before aggregating the answers. In these cases, you can use `ask_async` to submit the
image query and return immediately without waiting for an answer. You can then get an answer from
Groundlight later by calling `get_image_query` using the id from the `ImageQuery` object. returned
by ask_async.

## `submit_image_query`

`submit_image_query` provides the most configurability over submitting image queries. The other `ask_*` methods are actually wrappers around `submit_image_query` with some defaults set to produce their respective behavior.

See the details on the full function signature for `submit_image_query` and the other ask
groundlight methods in the [API Reference](/api-reference-docs/models.html#groundlight.Groundlight)
