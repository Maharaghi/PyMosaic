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

## Keys

### image_path
Change this to the path of the image you want to re-create.

### sub_image_dir
This is the folder of all the smaller images that will make up the main image.  
This folder can contain both .jpg and .png images.

### sub_image_size
This will be the dimensions of the small images.  
A lower size will of course make it harder to see.

### image_size_multiplier
This is a simply integer that will resize the main image.
Ex. If the `image_size_multiplier` is 8 and the image size is 1920x1080, the final image will have the dimensions 15360x8640.
