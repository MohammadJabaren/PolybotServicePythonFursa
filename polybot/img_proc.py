from pathlib import Path
from matplotlib.image import imread, imsave
import random


def rgb2gray(rgb):
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    return gray


class Img:

    def __init__(self, path):
        """
        Do not change the constructor implementation
        """
        self.path = Path(path)
        try:
            image = imread(path)
        except Exception as e:
            raise RuntimeError(f"Failed to read image from path '{path}': {e}")
        if image.ndim != 3 or image.shape[2] != 3:
            raise RuntimeError("Input image is not an RGB image")
        self.data = rgb2gray(image).tolist()

    def save_img(self):
        """
        Do not change the below implementation
        """
        new_path = self.path.with_name(self.path.stem + '_filtered' + self.path.suffix)
        try:
            imsave(new_path, self.data, cmap='gray')
            return new_path
        except Exception as e:
            raise RuntimeError(f"An error occurred while saving the image: {e}")

    def blur(self, blur_level=16):

        height = len(self.data)
        width = len(self.data[0])
        filter_sum = blur_level ** 2

        result = []
        for i in range(height - blur_level + 1):
            row_result = []
            for j in range(width - blur_level + 1):
                sub_matrix = [row[j:j + blur_level] for row in self.data[i:i + blur_level]]
                average = sum(sum(sub_row) for sub_row in sub_matrix) // filter_sum
                row_result.append(average)
            result.append(row_result)

        self.data = result

    def contour(self):
        for i, row in enumerate(self.data):
            res = []
            for j in range(1, len(row)):
                res.append(abs(row[j-1] - row[j]))

            self.data[i] = res


    def rotate(self):
        # TODO remove the `raise` below, and write your implementation
       # if not isinstance(self.data, list) or not all(isinstance(row, list) for row in self.data):
        #    raise RuntimeError("This image is not a grayscale image.")

        #if len(self.data) == 0:
         #   raise RuntimeError("The images is Empty.")

        row = len(self.data)
        col = len(self.data[0])

        new_matrix = [[0] * row for _ in range(col)]

        for i in range(row):
            for j in range(col):
                new_matrix[j][row - 1 - i] = self.data[i][j]

        self.data = new_matrix


    def salt_n_pepper(self):
        # TODO remove the `raise` below, and write your implementation
        #if not isinstance(self.data, list) or not all(isinstance(row, list) for row in self.data):
        #    raise RuntimeError("This image is not a grayscale image.")

        #if len(self.data) == 0:
        #    raise RuntimeError("The images is Empty.")


        for i in range(len(self.data)):
            for j in range(len(self.data[i])):
                random_value = random.random()
                if random_value < 0.2 :
                    self.data[i][j] = 255
                elif random_value > 0.8:
                    self.data[i][j] = 0


    def concat(self, other_img, direction='horizontal'):
        # TODO remove the `raise` below, and write your implementation
        #if not isinstance(other_img,Img):
        #    raise RuntimeError("Provided argument is not an image")

        #if not isinstance(self.data, list) or not all(isinstance(row, list) for row in self.data):
        #    raise RuntimeError("This image is not a grayscale image.")

        #if not isinstance(other_img.data, list) or not all(isinstance(row, list) for row in other_img.data):
        #    raise RuntimeError("The other image is not a grayscale image.")

        #if len(self.data) == 0 or len(other_img.data) == 0:
        #    raise RuntimeError("One of the images is empty.")

        if direction == 'horizontal':
            if len(self.data) != len(other_img.data):
                raise RuntimeError(
                    f"Images have different heights ({len(self.data)} != {len(other_img.data)}). Cannot concatenate horizontally."
                )
            self.data = [self.data[i] + other_img.data[i] for i in range(len(self.data))]

        elif direction == 'vertical':
            if len(self.data[0]) != len(other_img.data[0]):
                raise RuntimeError(
                    f"Images have different widths ({len(self.data[0])} != {len(other_img.data[0])}). Cannot concatenate vertically."
                )
            self.data = self.data + other_img.data

        else:
            raise RuntimeError(
                f"Invalid direction '{direction}' specified. Only 'horizontal' and 'vertical' are allowed.")




    def segment(self):
        # TODO remove the `raise` below, and write your implementation
       # if not isinstance(self.data, list) or not all(isinstance(row, list) for row in self.data):
       #     raise RuntimeError("This image is not a grayscale image.")

        #if len(self.data) == 0:
        #    raise RuntimeError("The images is Empty.")
        hundred = 100

        for i in range(len(self.data)):
            for j in range(len(self.data[i])):
                if self.data[i][j] > hundred:
                    self.data[i][j] = 255
                else:
                    self.data[i][j] = 0

    def inverse(self):

        for i in range(len(self.data)):
            for j in range(len(self.data[i])):
                self.data[i][j] = 255 - self.data[i][j]

    def gamma_correction(self):

        gamma = 2.2
        for i in range(len(self.data)):
            for j in range(len(self.data[i])):
                normalized = self.data[i][j] / 255.0
                corrected = pow(normalized, gamma)
                self.data[i][j] = min(255, max(0, round(corrected * 255)))

    def posterize(self):
        level = 4
        step = 255 // (level - 1)
        for i in range(len(self.data)):
            for j in range(len(self.data[0])):
                original = self.data[i][j]
                quantized = round(original / step) * step
                self.data[i][j] = min(255, max(0, quantized))

