class Piece:

    __slots__ = ["__imagefile","__type","__color"]

    def __init__(self,color,type):
        filename = ""
        filename += "assets/pixel chess/16x32 pieces/" + color+ "_" + type+ ".png"
        self.__color = color
        self.__imagefile = filename
        self.__type = type.lower()


    def get_type(self):
        return self.__type
    
    def image(self):
        return self.__imagefile
    
    def color(self):
        return self.__color
    def set_image(self,path):
        self.__imagefile = "C:/Users/myoce/Portfolio/Python-Projects/Chess/assets/pixel chess/16x32 pieces/" + self.__color + "_" + path

        
