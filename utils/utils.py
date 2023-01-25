
class Utils:
    @staticmethod
    def convertBinArrayToHexStr(array):
        return str(hex(int(''.join([str(x) for x in array]),2)))