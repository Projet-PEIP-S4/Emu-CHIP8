
class Utils:
    @staticmethod
    def convertBinArrayToHexStr(array):
        return hex(int(''.join([str(x) for x in array]),2))