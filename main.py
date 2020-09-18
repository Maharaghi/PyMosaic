import os
import glob
import json
import math
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = 1000000000

'''
TODO
Write a 5-Square algorithm to properly map out a pixel->sub-image conversion.
Split image into TL, TR, BL, BR, C directions with mean value
'''


def exitWithEnter():
  input("Press enter to quit the program")
  exit(0)

if not os.path.exists("settings.json"):
  print("settings.json DOES NOT EXIST, A DEFAULT ONE WILL BE CREATED! PLEASE ENTER INFORMATION THERE!")
  with open("settings.json", "w") as f:
    obj = {
      "image_path": "C:/Path/To/Image",
      "sub_image_dir": "C:/Path/To/Sub-Images",
      "sub_image_size": 32,
      "image_size_multiplier": 4
    }
    json.dump(obj, f)
  exitWithEnter()

with open("settings.json", "r") as f:
  settings = json.load(f)
  impath = settings.get("image_path")
  mosaic_dir = settings.get("sub_image_dir")
  if impath is None or mosaic_dir is None:
    print("image_path or sub_image_dir DOES NOT EXIST IN THE SETTINGS FILE! PLEASE MODIFY THIS FILE SO IT CONTAINS BOTH!")
    exitWithEnter()
  elif not os.path.exists(impath):
    print("Image {} does not exist!".format(impath))
    exitWithEnter()
  elif os.path.isdir(impath):
    print("Input image path cannot be a directory!")
    exitWithEnter()
  elif not os.path.exists(mosaic_dir):
    print("Sub-image directory {} does not exist!".format(mosaic_dir))
    exitWithEnter()
  elif not os.path.isdir(mosaic_dir):
    print("Sub-image path {} does not point to a directory!".format(mosaic_dir))
    exitWithEnter()
  elif not settings.get("sub_image_size"):
    print("Key 'sub_image_size' not set in settings.json!")
    exitWithEnter()
  elif not settings.get("image_size_multiplier"):
    print("Key 'image_size_multiplier' not set in settings.json")
    exitWithEnter()
  
  try:
    MOS_SIZE_X = int(settings.get("sub_image_size"))
  except:
    print("'sub_image_size' in settings.json has to be an integer!")
    exitWithEnter()
  
  try:
    MMOD = int(settings.get("image_size_multiplier"))
  except:
    print("'sub_image_size' in settings.json has to be an integer!")
    exitWithEnter()

  MOS_SIZE_X_SCALED = max(MOS_SIZE_X // MMOD, 2)
  if MOS_SIZE_X / MMOD < 2:
    print("Because the 'sub_image_size' is smaller than twice the size of 'image_size_multiplier' the 'sub_image_size' will be set to {}".format(MMOD))

  if (MOS_SIZE_X / MMOD) % 1 != 0:
    print("Because the 'sub_image_size' is not divisible by 'image_size_multiplier' the 'sub_image_size' will be set to {}".format(MOS_SIZE_X_SCALED*MMOD))
  
  MOS_SIZE_X = MOS_SIZE_X_SCALED
  MOS_SIZE_Y = MOS_SIZE_X_SCALED
  
os.makedirs("./exports", exist_ok=True)

MOSAIC_DIR = settings["sub_image_dir"]

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
  def __init__(self, image, filename):
    self.colorDict = dict()
    self.runtimeDict = dict()
    self.image = image
    self.filename = filename

    self.colorDict["TL"] = dict()
    self.colorDict["TR"] = dict()
    self.colorDict["BL"] = dict()
    self.colorDict["TR"] = dict()
    self.colorDict["C"] = dict()

    exportdir = os.path.basename(settings["sub_image_dir"])
    if os.path.exists("./exports/EX_{}_export_{}.json".format(exportdir, MOS_SIZE_X*MMOD)):
      print("Found existing export data for current size, loading data...")
      with open("./exports/EX_{}_export_{}.json".format(exportdir, MOS_SIZE_X*MMOD), "r") as f:
        keys = json.load(f)
        for key in keys.keys():
          objs = keys[key]
          for obj in objs:
            self.colorDict[key][(int(obj["key"][0]), int(obj["key"][1]), int(obj["key"][2]))] = obj["val"]

        del keys
    else:
      print("No existing export data found, mapping sub-images.")
      self.map_mosaic()
      print("Mapping finished! Exporting data...")
      objs = []
      for key in self.colorDict.keys():
        for colour_key in self.colorDict[key]:
          obj = {
            "key": list(colour_key),
            "val": self.colorDict[key]
          }
          objs.append(obj)
      try:
        with open("./exports/EX_{}_export_{}.json".format(exportdir, MOS_SIZE_X*MMOD), "w") as f:
          json.dump(objs, f, indent=2, cls=NumpyArrayEncoder)
        del objs
        self.colorDict = self.runtimeDict
      except:
        print("FATAL: Could not write json file.")
        exitWithEnter()
        return
      print("Data exported!")
    
    print("Data loaded, running on image!")

    self.im_to_mosaic()

  def map_mosaic(self):
    l = len(files)
    self.printProgressBar(0, l, prefix="Mapping images:", suffix="Complete", length=50)
    for idx, file in enumerate(files):
      try:
        temp = Image.open(file)
        labIm = temp.resize((MOS_SIZE_X * MMOD, MOS_SIZE_Y * MMOD), resample=Image.ANTIALIAS).convert('YCbCr')
        temp.close()
      except:
        print(f"Could not open image with path {file}")
        continue

      width, height = labIm.size

      for y in range(2):
        for x in range(2):
          crop = labIm.crop((x * width//2, y * height//2, x * width//2 + width//2, y * height//2 + height//2))
          key = "T" if y == 0 else "B"
          key = key + "L" if x == 0 else "R"
          
          bw, cb, cr = crop.split()
          
          imColor = self.get_mean_color(bw, cb, cr)
      
          self.colorDict[key][imColor] = file
          self.runtimeDict[key][imColor] = np.asarray(labIm)
        
      crop = labIm.crop((x * width//4, y * height//4, x * width//4 + width//2, y * height//4 + height//2))
      bw, cb, cr = crop.split()
      imColor = self.get_mean_color(bw, cb, cr)
      self.colorDict["C"][imColor] = file
      self.runtimeDict["C"][imColor] = np.asarray(labIm)
      
      self.printProgressBar(idx+1, l, prefix="Mapping images:", suffix="Complete", length=50)


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
    
    l = x_split * y_split
    self.printProgressBar(0, l, prefix="Creating image:", suffix="Complete", length=50)
    for y in range(y_split):
      for x in range(x_split):
        # Split the image into the size of each sub-image
        ic = self.split_and_mean(x, y, reg_im)
        if (ic == False):
          continue

        y_c, x_c = np.where(np.all(ic != (-1, -1, -1), axis=-1))
        imArray[y_c + (y*MOS_SIZE_Y*MMOD), x_c + (x*MOS_SIZE_X*MMOD)] = ic[y_c, x_c]
        self.printProgressBar((x_split * y) + x, l, prefix="Creating image:", suffix="Complete", length=50)

    # Finish progress bar
    self.printProgressBar(l, l, prefix="Creating image:", suffix="Complete", length=50)
    
    name = os.path.splitext(self.filename)
    print("Saving image as {}_{}_{}.png".format(name[0], MMOD, MMOD*MOS_SIZE_X))
    Image.fromarray(imArray, mode="YCbCr").convert("RGB").save("{}_{}_{}.png".format(name[0], MMOD, MMOD*MOS_SIZE_X))

  def split_and_mean(self, x, y, reg_im):
    for ix, key in enumerate(("TL", "TR", "BL", "BR", "C")):


      bw = reg_im[y * MOS_SIZE_Y:y * MOS_SIZE_Y + MOS_SIZE_Y, x * MOS_SIZE_X:x * MOS_SIZE_X + MOS_SIZE_X, 0]
      cb = reg_im[y * MOS_SIZE_Y:y * MOS_SIZE_Y + MOS_SIZE_Y, x * MOS_SIZE_X:x * MOS_SIZE_X + MOS_SIZE_X, 1]
      cr = reg_im[y * MOS_SIZE_Y:y * MOS_SIZE_Y + MOS_SIZE_Y, x * MOS_SIZE_X:x * MOS_SIZE_X + MOS_SIZE_X, 2]

      # Get the mean colour of this part of the image
      imColor = self.get_mean_color(bw, cb, cr)

      # If we have the sub-image stored for this colour we can simply use that immediately
      if (self.colorDict.get(imColor) is not None):
        ic = self.colorDict.get(imColor)
        if type(ic) == str:
          try:
            temp = Image.open(ic)
            # Resize image, convert to LAB format, and make into numpy array
            ic = np.asarray(temp.resize((MOS_SIZE_X * MMOD, MOS_SIZE_Y * MMOD), resample=Image.ANTIALIAS).convert('YCbCr'))
            temp.close()
            
            # Save numpy array to colorDict so we don't have to read image twice
            self.colorDict[imColor] = ic
          except:
            print(f"Could not open image with path {ic}")
            return False

          return ic
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
        if type(ic) == str:
          try:
            temp = Image.open(ic)
            # Resize image, convert to LAB format, and make into numpy array
            ic = np.asarray(temp.resize((MOS_SIZE_X * MMOD, MOS_SIZE_Y * MMOD), resample=Image.ANTIALIAS).convert('YCbCr'))
            temp.close()
          except:
            print(f"Could not open image with path {ic}")
            return False

        # Add this colour to the dictionary so we don't have to run calculations again for this colour
        self.colorDict[(imColor[0], imColor[1], imColor[2])] = ic

        return ic

  # Return the median colour as an int tuple
  def get_mean_color(self, bw, cb, cr):
    bw_max = np.mean(bw)

    cb_max = np.mean(cb)

    cr_max = np.mean(cr)

    imColor = (int(bw_max), int(cb_max), int(cr_max))
    return imColor

  # CREDIT: https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
  # Print iterations progress. 
  def printProgressBar (self, iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% ({iteration}/{total}) {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()


if __name__ == "__main__":
  IMPATH = settings["image_path"]
  filename = os.path.basename(IMPATH)
  t = Image.open(IMPATH) 
  im = t.convert('YCbCr')
  t.close()

  creator = MosaicCreator(im, filename)