class Square:

    __slots__ = ["__piece","__position"]

    def __init__(self,position):
        self.__position = position
        self.__piece = None

    def get_piece(self):
        return self.__piece

    def get_position(self):
        return self.__position
    
    def move_piece(self):
        if self.__piece != None:
            temp = self.__piece
            self.__piece = None
            return temp
        return None
    
    def set_piece(self,piece):
        self.__piece = piece

    