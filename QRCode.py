

import pyqrcode
import qrcode
import cv2

qr = qrcode.make('Dieser QR Code stellt die für den Impfnachweis nötigen Impfadaten dar')
qr.save('Test.png')
qr.show()
d = cv2.QRCodeDetector()
d.detectAndDecode(cv2.imread('Test.png'))
val, points, straight_qrcode = d.detectAndDecode(cv2.imread('Test.png'))
print(val)







    # for objects in decodedObjects:
    #     bytstr = objects.data
    #     dictstr = bytstr.decode('utf-8')
    #     certificate_data = ast.literal_eval(dictstr)
     # new_entry = Proof_of_vaccination(unique_certificate_identifier = '3', f_name =certificate_data['f_name'], date_of_vaccination = certificate_data['date_of_vaccination'], vaccine = certificate_data['vaccine'], batch_number=certificate_data['batch_number'], vaccine_category=certificate_data['vaccine_category'], unique_issuer_identifier=certificate_data['certificate_issuer'], disease= certificate_data['disease'], vaccine_marketing_authorization_holder= certificate_data['vaccine_marketing_authorization_holder'], issued_at= certificate_data['issued_at'])
        # db.session.add(new_entry)
        # db.session.commit()