import random

from PIL import Image, ImageEnhance, ImageOps


class ImageTransform:
    def __init__(self):
        self.used_transforms = set()

    def random_rotate(self, img):
        if "random_rotate" not in self.used_transforms:
            angle = random.randint(-25, 25)
            self.used_transforms.add("random_rotate")
            return img.rotate(angle)
        return img

    def random_shift(self, img):
        if "random_shift" not in self.used_transforms:
            x_shift = random.randint(-10, 10)
            y_shift = random.randint(-10, 10)
            self.used_transforms.add("random_shift")
            return img.transform(img.size, Image.AFFINE, (1, 0, x_shift, 0, 1, y_shift))
        return img

    def random_scale(self, img):
        if "random_scale" not in self.used_transforms:
            scale_factor = random.uniform(0.9, 1.1)
            width, height = img.size
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            img = img.resize((new_width, new_height))
            self.used_transforms.add("random_scale")
            return img.crop((0, 0, width, height))
        return img

    def horizontal_flip(self, img):
        if "horizontal_flip" not in self.used_transforms:
            self.used_transforms.add("horizontal_flip")
            return ImageOps.mirror(img)
        return img

    def color_jitter(self, img):
        if "color_jitter" not in self.used_transforms:
            brightness_factor = random.uniform(0.7, 1.3)
            contrast_factor = random.uniform(0.7, 1.3)
            img = ImageEnhance.Brightness(img).enhance(brightness_factor)
            img = ImageEnhance.Contrast(img).enhance(contrast_factor)
            self.used_transforms.add("color_jitter")
            return img
        return img
    
    def random_shear(self, img):
        if 'random_shear' not in self.used_transforms:
            max_shear_left = -0.3
            max_shear_right = 0.3
            shear_factor = random.uniform(max_shear_left, max_shear_right)

            width, height = img.size
            m = -shear_factor  # Negative value for reverse shear

            # Shearing in x-direction
            img = img.transform((width, height), Image.AFFINE, (1, m, 0, 0, 1, 0))
            self.used_transforms.add('random_shear')
            return img
        return img

