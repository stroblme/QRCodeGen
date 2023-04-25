# pip3 install qrcode

# import essential libraries
import qrcode

# libraries for rounded corners
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer
from qrcode.image.styles.colormasks import RadialGradiantColorMask

# library for logo creation
from PIL import Image

# example data of the website or application
data = input('Enter the URL you want to encode: ')


# open logo
# logo = Image.open('logo.png')

# taking base width
base_width = 100

# # adjust image size
# width_percent = (base_width / float(logo.size[0]))
# hSize = int((float(logo.size[1]) * float(width_percent)))
# logo = logo.resize((base_width, hSize), Image.ANTIALIAS)

# instantiate QRCode object
QR = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=20)

# add data to qr code
QR.add_data(data)

# generate qr code
QR.make(fit=True)

# transfer the array into an actual image
img = QR.make_image(image_factory=StyledPilImage,
                    module_drawer=RoundedModuleDrawer(),
                    color_mask=RadialGradiantColorMask(center_color=(143, 82, 182), edge_color=(41, 25, 118)))

# # set size of QR code
# pos = ((img.size[0] - logo.size[0]) // 2,
#        (img.size[1] - logo.size[1]) // 2)

# paste logo in QR code
# img.paste(logo, pos)
# save img to a file
img.save('myQR_code.png')
print('Your QR code have been generated successfully!')