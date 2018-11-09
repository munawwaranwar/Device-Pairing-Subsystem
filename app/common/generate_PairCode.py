import string
from random import *
from app import conf
from app.Models.pairing_codes import Pairing_Codes

def gen_paircode():

    try:
        #min_char, max_char = 6, 8

        paircode_exist = True

        while paircode_exist == True:

            all_char = string.ascii_letters + string.digits

            # paircode = "".join(choice(all_char) for x in range(randint(min_char,max_char)))
            paircode = "".join(choice(all_char) for x in range(conf['pc_length']))

            chk = Pairing_Codes.query.filter(Pairing_Codes.pair_code == '{}'.format(paircode)).first()

            if chk:

                paircode_exist = True

            else:

                paircode_exist = False


        return paircode

    except Exception as e:

        return


