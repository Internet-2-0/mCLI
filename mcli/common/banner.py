import base64
import inspect
import random

from mcli.lib.settings import VERSION


class Banner(object):

    def banner_1(self):
        print("""

\033[91m   _____         .__                                       _________ .____    .___
  /     \ _____  |  |   ____  ___________   ____           \_   ___ \|    |   |   |
 /  \ /  \\\\__  \ |  | _/ ___\/  _ \_  __ \_/ __ \   ______ /    \  \/|    |   |   |
/    Y    \/ __ \|  |_\  \__(  <_> )  | \/\  ___/  /_____/ \     \___|    |___|   |\033[0m\033[94m
\____|__  (____  /____/\___  >____/|__|    \___  >          \______  /_______ \___|
        \/     \/          \/                  \/                  \/        \/    \033[0m
""")

    def banner_2(self):
        print("""\033[91m                              ,--,            
                           ,---.'|            
          ____    ,----..  |   | :      ,---, \033[0m
        ,'  , `. /   /   \ :   : |   ,`--.' | 
     ,-+-,.' _ ||   :     :|   ' :   |   :  : 
  ,-+-. ;   , ||.   |  ;. /;   ; '   :   |  ' \033[91m
 ,--.'|'   |  ||.   ; /--` '   | |__ |   :  | 
|   |  ,', |  |,;   | ;    |   | :.'|'   '  ; 
|   | /  | |--' |   : |    '   :    ;|   |  | \033[0m
|   : |  | ,    .   | '___ |   |  ./ '   :  ; 
|   : |  |/     '   ; : .'|;   : ;   |   |  ' 
|   | |`-'      '   | '/  :|   ,/    '   :  | \033[91m
|   ;/          |   :    / '---'     ;   |.'  
'---'            \   \ .'            '---'    
                  `---`                       \033[0m
""")

    def banner_3(self):
        print("""\033[91m
  __  __       _                    
 |  \/  |     | |                   
 | \  / | __ _| | ___ ___  _ __ ___ 
 | |\/| |/ _` | |/ __/ _ \| '__/ _ \\
 | |  | | (_| | | (_| (_) | | |  __/
 |_|  |_|\__,_|_|\___\___/|_|  \___|                           
\033[0m""")

    def banner_4(self):
        print("""\033[91m                                      
             `^                      ^`           
             "*t^                  ^t*"           
             "***t^              ^t***"           
             "*****t^          ^t*****"           
             "*******t^      ^t*******"           
             "*********t^  ^t*********"           
       "<~~~~i/zzzzzzzzzzttzzzzzzzzzz/i~~~~<"     
       <*****< ^/******************/^ >*****<     
       <*****<   ^/**************/^   >*****<     
       <*****1.    ^/**********/^    .1*****<     
       <******v!.    ^/******/^    .!v******<     
       <********v!.    ^/**/^    .!v********<     
       <**********v`     ^^     `v**********<     
       <*********{'              '{*********<     
       <*******{'                  '{*******<     
       ,]]]]]_'                      '_]]]]], \033[0m                                                                                                                                                                                                                                                                                                                                
""")

    def banner_5(self):
        print("""
\033[94m::::::     .:::::              :::\033[0m                                                 
\033[91m::::::.    ::::::              :::                                                 
:::::::   :::::::   .:::::::.  :::   .:::::::.    :::::::.   :::..:::  .:::::::.   
:::..::: .:::.:::  .::.   :::. :::  ::::   :::. .:::.  .:::. :::::... :::.   .:::\033[0m    
:::. :::.::: .:::   ...::::::. ::: .:::         :::.    .::: ::::    .:::::::::::
:::.  :::::. .:::  :::.   :::. ::: .:::     .   :::.    .::: :::.    .:::.         
:::.  .::::  .::: .:::.  ::::. :::  ::::...:::. .:::....:::  :::.     ::::. .::::  
.::.   :::   .:::  .:::::.:::. :::   .::::::.     .::::::.   :::.      .::::::.. 
\033[0m""")


class Saying(object):

    encode_it = random.SystemRandom().randint(1, 5) > 3

    def saying_1(self):
        print('From all the way in the back of the food stamp line ...')

    def saying_2(self):
        saying_str = 'VT Still Sucks ...'
        if self.encode_it:
            print(base64.b64encode(saying_str.encode()).decode())
        else:
            print(saying_str)

    def saying_3(self):
        print("Where even the nastiest bugs get a timeout to think about their life choices")

    def saying_4(self):
        saying_str = f'Version: {VERSION}'
        if self.encode_it:
            print(base64.b64encode(saying_str.encode()).decode())
        else:
            print(saying_str)

    def saying_5(self):
        saying_str = "Simple File Analysis"
        if self.encode_it:
            print(base64.b64encode(saying_str.encode()).decode())
        else:
            print(saying_str)

    def saying_6(self):
        print("If APT-41 was a pasta, they'd be angel hair ...")

    def saying_7(self):
        saying_str = "nop\nn:\to:\tp:\n0x90"
        if self.encode_it:
            print(base64.b64encode(saying_str.encode()).decode())
        else:
            print(saying_str)

    def saying_8(self):
        print("Ooooo, you're hacking (I'm going to tell on you) ...!")

    def saying_9(self):
        print("'The only RE tool that doesn't make you want to sleep' - Malcore")

    def saying_10(self):
        print("Undefined symbol 'r_anal_fisting'")

    def saying_11(self):
        print('{"we": "only", "accept": "json", "here"}')

    def saying_12(self):
        print('Wake up!\nWAke up!\nWAKe up!\nWAKE up!\nWAKE Up!\nWAKE UP!')

    def saying_13(self):
        print("\033[94mconst *char\033[0m \033[30mreality="
              "\033[0m'\033[92m\\x41\\x41\\x41\\x41\\x41\\x41\\x41\\x41\\x41';\033[0m")


def banner_choice():
    """
    execute the banner randomly this way it's not always the same
    :return:
    """
    banner_class = Banner()
    saying_class = Saying()
    banner_method_names = [attr for attr in dir(banner_class) if inspect.ismethod(getattr(banner_class, attr))]
    saying_method_names = [attr for attr in dir(saying_class) if inspect.ismethod(getattr(saying_class, attr))]
    exec(f'banner_class.{random.SystemRandom().choice(banner_method_names)}()')
    exec(f'saying_class.{random.SystemRandom().choice(saying_method_names)}()')
    print("\n\n")
