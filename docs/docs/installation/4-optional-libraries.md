# Optional libraries

## Smaller is better!

The Groundlight Python SDK is optimized to run on small edge devices. As such, you can use the Groundlight SDK without
installing large libraries like `numpy` or `OpenCV`.

But if you're already installing them, we'll use them. Our SDK detects if these libraries are installed
and will make use of them if they're present. If not, we'll gracefully degrade, and tell you what's
wrong if you try to use these features.

## PIL - optional but default installed

The `PIL` library offers a bunch of standard utilities for working with images in python. The Groundlight SDK can work without `PIL`.

Because `PIL` is not very large, and is quite useful, we install it by default with the normal build of the Groundlight SDK. So when you

```shell
pip3 install groundlight
```

it comes with the `pillow` version of the `PIL` library already installed.

### Working without PIL

If you are extremely space constrained, you can install the Groundlight SDK from source without `PIL` and it will work properly, but with reduced functionality.
Specifically, you will need to convert your images into `JPEG` format yourself. The SDK normally relies on `PIL` to do JPEG compression (which is a non-trivial algorithm), and the API requires images to be in JPEG format. However on space-constrained platforms, sometimes this conversion is done in hardware, and so we don't want to force you to install `PIL` if you don't need it.

## Numpy, OpenCV - fully optional

These commonly-used libraries are not installed by default, because they are quite large, and their installation can often cause conflicts with other dependent libraries. If you want to use them, install them directly.
