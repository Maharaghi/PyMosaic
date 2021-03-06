# PyMosaic

This is a simple program I made because I just wanted to see if I could.
I tried optimizing it a bit, but it's probably far from good.

You can set the sub-image size and the main image size multiplier in the settings.json that is created on launch.  
If for some reason the settings.json file isn't created, here is a default file:
```
{
  "image_path": "C:/Path/To/Image",
  "sub_image_dir": "C:/Path/To/Sub-Images",
  "sub_image_size": 32,
  "image_size_multiplier": 4
}
```

## Settings

### image_path
Change this to the path of the image you want to re-create.

### sub_image_dir
This is the folder of all the smaller images that will make up the main image.  
This folder can contain both .jpg and .png images.

### sub_image_size
This will be the dimensions of the small images.  
A lower size will of course make it harder to see.

### image_size_multiplier
This is simply an integer that will be applied to resize the main image.
Ex. If the `image_size_multiplier` is 8 and the image size is 1920x1080, the final image will have the dimensions 15360x8640.

## Running the program
To run this program simply clone the repository using  
`git clone https://github.com/Maharaghi/PyMosaic.git`  
install dependencies using `pip install -r requirements.txt`  
and then run it once with `python main.py`.  
After that simply modify the created `settings.json` according to the keys above, and then run `python main.py` again.

## Example
Original image  
![Original image](example.jpg)

Mosaic image (sub_image_size is 32 and image_size_multiplier is 16)
![Mosaic image](example_16_32.png)
