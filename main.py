import os
import glob
import json
import math
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = 1000000000

MOSAIC_DIR = r"C:\Path\To\Sub-Images"

MOS_SIZE_X = 1
MOS_SIZE_Y = 1

MMOD = 16

files = glob.glob(MOSAIC_DIR + '/**/*.png', recursive=True)
files_jpg = glob.glob(MOSAIC_DIR + '/**/*.jpg', recursive=True)
files.extend(files_jpg)

print("Will use a list of {} sub-images".format(len(files)))

class NumpyArrayEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, np.integer):
      return int(obj)
    elif isinstance(obj, np.floating):
      return float(obj)
    elif isinstance(obj, np.ndarray):
      return obj.tolist()
    else:
      return super(NumpyArrayEncoder, self).default(obj)

class MosaicCreator():
  def __init__(self, image):
    self.colorDict = dict()
    self.image = image


    if os.path.exists("export_{}.json".format(MOS_SIZE_X*MMOD)):
      with open("export_{}.json".format(MOS_SIZE_X*MMOD), "r") as f:
        objs = json.load(f)
        for obj in objs:
          self.colorDict[(int(obj["key"][0]), int(obj["key"][1]), int(obj["key"][2]))] = np.reshape(obj["val"], (MOS_SIZE_Y*MMOD, MOS_SIZE_X*MMOD, 3))
        del objs
    else:
      self.map_mosaic()
      objs = []
      for key in self.colorDict.keys():
        obj = {
          "key": list(key),
          "val": self.colorDict[key]
        }
        objs.append(obj)
      try:
        with open("export_{}.json".format(MOS_SIZE_X*MMOD), "w") as f:
          json.dump(objs, f, indent=2, cls=NumpyArrayEncoder)
        del objs
      except:
        print("Could not write json file")

    self.im_to_mosaic()

  def map_mosaic(self):
    for file in files:
      try:
        temp = Image.open(file)
        labIm = temp.resize((MOS_SIZE_X * MMOD, MOS_SIZE_Y * MMOD), resample=Image.ANTIALIAS).convert('YCbCr')
        temp.close()
      except:
        continue


      bw, cb, cr = labIm.split()

      imColor = self.get_mean_color(bw, cb, cr)

      self.colorDict[imColor] = np.asarray(labIm)

  def im_to_mosaic(self):
    if not self.image:
      return
    
    width, height = self.image.size

    print("Image width is {} and height is {}".format(width, height))

    x_split = width // MOS_SIZE_X
    y_split = height // MOS_SIZE_Y

    reg_im = self.image.resize((x_split * MOS_SIZE_X, y_split * MOS_SIZE_Y), resample=Image.ANTIALIAS)
    im = self.image.resize((x_split * MOS_SIZE_X * MMOD, y_split * MOS_SIZE_Y * MMOD), resample=Image.ANTIALIAS)

    reg_im = np.asarray(reg_im).copy()
    imArray = np.asarray(im).copy()

    for y in range(y_split):
      for x in range(x_split):
        # Split the image into the size of each sub-image
        bw = reg_im[y * MOS_SIZE_Y:y * MOS_SIZE_Y + MOS_SIZE_Y, x * MOS_SIZE_X:x * MOS_SIZE_X + MOS_SIZE_X, 0]
        cb = reg_im[y * MOS_SIZE_Y:y * MOS_SIZE_Y + MOS_SIZE_Y, x * MOS_SIZE_X:x * MOS_SIZE_X + MOS_SIZE_X, 1]
        cr = reg_im[y * MOS_SIZE_Y:y * MOS_SIZE_Y + MOS_SIZE_Y, x * MOS_SIZE_X:x * MOS_SIZE_X + MOS_SIZE_X, 2]

        # Get the mean colour of this part of the image
        imColor = self.get_mean_color(bw, cb, cr)

        # If we have the sub-image stored for this colour we can simply use that immediately
        if (self.colorDict.get(imColor) is not None):
          ic = self.colorDict.get(imColor)
          y_c, x_c = np.where(np.all(ic != (-1, -1, -1), axis=-1))
          imArray[y_c + (y*MOS_SIZE_Y*MMOD), x_c + (x*MOS_SIZE_X*MMOD)] = ic[y_c, x_c]

        # Else try to get the closest colour
        else:
          setColour = (0, 0, 0)
          imColor = np.array(imColor)
          colours = list(self.colorDict.keys())

          sub_colours = np.array(colours) - imColor

          diffs = np.linalg.norm(sub_colours, axis=-1)
          index = diffs.argmin()
          setColour = colours[index]

          ic = self.colorDict.get((setColour[0], setColour[1], setColour[2]))

          # Add this colour to the dictionary so we don't have to run calculations again for this colour
          self.colorDict[(imColor[0], imColor[1], imColor[2])] = ic

          y_c, x_c = np.where(np.all(ic != (-1, -1, -1), axis=-1))
          imArray[y_c + (y*MOS_SIZE_Y*MMOD), x_c + (x*MOS_SIZE_X*MMOD)] = ic[y_c, x_c]

    Image.fromarray(imArray, mode="YCbCr").convert("RGB").save("IM_{}_{}.png".format(MMOD, MMOD*MOS_SIZE_X))

  # Return the median colour as an int tuple
  def get_mean_color(self, bw, cb, cr):
    bw_max = np.mean(bw)

    cb_max = np.mean(cb)

    cr_max = np.mean(cr)

    imColor = (int(bw_max), int(cb_max), int(cr_max))
    return imColor


if __name__ == "__main__":
  IMPATH = r"C:\Path\To\Image.png|jpg"
  t = Image.open(IMPATH) 
  im = t.convert('YCbCr')
  t.close()

  creator = MosaicCreator(im)