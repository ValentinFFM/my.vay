

import pyqrcode
import qrcode
import png
import cv2

qr = qrcode.make('Dieser QR Code stellt die für den Impfnachweis nötigen Impfadaten dar')
qr.save('Test.png')
qr.show()
d = cv2.QRCodeDetector()
d.detectAndDecode(cv2.imread('Test.png'))
val, points, straight_qrcode = d.detectAndDecode(cv2.imread('Test.png'))
print(val)






