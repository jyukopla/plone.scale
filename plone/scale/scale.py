import sys
from cStringIO import StringIO
import PIL.Image
import PIL.ImageFile

# Set a larger buffer size. This fixes problems with jpeg decoding.
# See http://mail.python.org/pipermail/image-sig/1999-August/000816.html for
# details.
PIL.ImageFile.MAXBLOCK = 1000000


def scaleImage(image, width=None, height=None, direction="down"):
    """Scale an image to another size.

    The generated image is a JPEG image, unless the original is a PNG
    image. This is needed to make sure alpha channel information is
    not lost, which JPEG does not support.

    Scaling can happen in two directions: `up` scaling scales the smallest
    dimension up to the required size, while `down` scaling starts by
    scaling the largest dimension to the required size. This differences
    can be very important. For logos use `up` scaling, while normal
    photo usage in CMS contexts usually requires `down` scaling.

    The return value is a tuple with the new image, the image format
    and a size-tuple.
    """
    if width is None and height is None:
        raise ValueError("Either width or height need to be given")

    image=PIL.Image.open(StringIO(image))

    if image.mode=="1":
        # Convert black&white to grayscale
        image=image.convert("L")
    elif image.mode=="P":
        # Convert palette based images to 3x8bit+alpha
        image=image.convert("RGBA")

    # When we create a new image during scaling we loose the format
    # information, so remember it here.
    image_format=image.format

    current_size=image.size
    # Determine scale factor needed to get the right height
    if height is None:
        scale_height=None
    else:
        scale_height=(float(height)/float(current_size[1]))
    if width is None:
        scale_width=None
    else:
        scale_width=(float(width)/float(current_size[0]))

    if scale_height==scale_width:
        # The original already has the right aspect ratio, so we only need
        # to scale.
        image.thumbnail((width, height), PIL.Image.ANTIALIAS)
    else:
        if direction=="down":
            if scale_height is None or (scale_width is not None and scale_width>scale_height):
                # Width is the smallest dimension (relatively), so scale up
                # to the desired width
                new_width=width
                new_height=int(round(current_size[1]*scale_width))
            else:
                new_height=height
                new_width=int(round(current_size[0]*scale_height))
        else:
            if scale_height is None or (scale_width is not None and scale_width<scale_height):
                # Width is the largest dimension (relatively), so scale up
                # to the desired width
                new_width=width
                new_height=int(round(current_size[1]*scale_width))
            else:
                new_height=height
                new_width=int(round(current_size[0]*scale_height))

        image.draft(image.mode, (new_width, new_height))
        image=image.resize((new_width, new_height), PIL.Image.ANTIALIAS)

        if (width is not None and new_width>width) or (height is not None and new_height>height):
            if width is None:
                left=0
                right=new_width
            else:
                left=int((new_width-width)/2.0)
                right=left+width
            if height is None:
                height=new_height
            image=image.crop((left, 0, right, height))

    result=StringIO()

    if image_format=="PNG":
        format="PNG"
    else:
        format="JPEG"

    image.save(result, format, quality=88, optimize=True)
    result.seek(0)

    return (result.getvalue(), format, image.size)

