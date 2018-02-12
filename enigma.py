import numpy as np
import time


class Enigma(object):
    # -------------------------------------------------------------------------
    # --------------------------- SETUP ---------------------------------------
    # -------------------------------------------------------------------------
    def __init__(self,
                 seed=0,
                 nRotors='rand',
                 evenBounce=True,
                 charSet='default'):

        np.random.seed(seed)
        # ADD ERROR CHECKING

        self.charSet, self.nChar = self.__get_char_set(charSet)
        self.reflector = self.__build_reflector(evenBounce)
        self.rotors = self.__build_rotors(nRotors)
        self.movement = self.__set_movement()
        self.offset = np.random.randint(0, self.nChar, size=len(self.rotors))
        return None

    def __get_char_set(self, charSet):
        if charSet == 'default':
            self.charSet = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I',
                            'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R',
                            'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', ' ')
        else:
            self.charSet = charSet
        return self.charSet, len(self.charSet)

    def __build_reflector(self, evenBounce):
        nBounce = self.__bounce(evenBounce)

        r = np.arange(self.nChar)
        np.random.shuffle(r)

        ref = {}
        pairLen = int((self.nChar - nBounce) / 2)
        for i in range(pairLen):
            ref[r[i]] = r[(i+1)*-1]
            ref[r[(i+1)*-1]] = r[i]

        for i in range(pairLen, pairLen+nBounce):
            ref[r[i]] = r[i]
            # return ref

        for i in range(self.nChar):
            r[i] = ref[i]
        return r

    def __build_rotors(self, nRotors):
        if nRotors == 'rand':
            nRotors = int(np.random.uniform(3, 50))
        else:
            nRotors = nRotors
            # ADD ERROR CHECKING
        rotors = [np.arange(self.nChar) for i in range(nRotors)]
        for i in range(nRotors):
            np.random.shuffle(rotors[i])
        return rotors

    def __bounce(self, evenBounce):
        if self.nChar % 2:  # If odd
            nBounce = 1
        else:  # If even
            if evenBounce:
                nBounce = 2
            else:
                nBounce = 0
        return nBounce

    def __set_movement(self):
        primeList = np.array([1, 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37,
                              41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89,
                              97, 101, 103, 107, 109, 113, 127, 131, 137, 139,
                              149, 151, 157, 163, 167, 173, 179, 181, 191,
                              193, 197, 199, 211, 223, 227])
        np.random.shuffle(primeList)
        return np.remainder(primeList[0:len(self.rotors)], self.nChar)

    # -------------------------------------------------------------------------
    # ---------------------- ENCODING/DECODING --------------------------------
    # -------------------------------------------------------------------------
    def encode(self):
        message = ''
        for n in self.message:
            char = self.charSet.index(n)

            # Feed character through rotors
            for i, rotor in enumerate(self.rotors):
                char = self.feed_forward(char, i, rotor)

            # Feed character through reflector
            char = self.reflect(char)

            # Feed character back through rotors
            for i, rotor in enumerate(self.rotors[::-1]):
                char = self.feed_back(char, i, rotor)

            # Record output
            message = ''.join([message, self.charSet[char]])

            # Update rotor setting
            self.turn_rotors()
        return message

    def feed_forward(self, char, i, rotor):
        char = rotor[(char + self.offset[i]) % self.nChar]
        return char

    def reflect(self, char):
        char = self.reflector[char]
        return char

    def feed_back(self, char, i, rotor):
        char = np.where(rotor == char)
        return (int(char[0]) - self.offset[-(i+1)]) % self.nChar

    def turn_rotors(self):
        self.offset = (self.offset + self.movement) % self.nChar
        return None

    # -------------------------------------------------------------------------
    # ------------------ MESSAGE CONSTRUCTION ---------------------------------
    # -------------------------------------------------------------------------
    def get_input(self):
        self.get_message()
        self.add_padding()
        self.rand_insert()
        print('Your message will be encoded as: \n{}'.format(self.message))
        return None

    def get_message(self, max_len=250):
        message = input("Enter your message: ")
        message_len = len(message)
        while message_len > max_len:
            print("Your message exceeds 250 characters.")
            message = input("Please reenter your message:")
            message_len = len(message)
        self.message = message.upper()
        return None

    def add_padding(self, nbuff=3, buffchar=' '):
        self.message = ''.join([nbuff*buffchar, self.message, nbuff*buffchar])
        return None

    def rand_insert(self, total_len=256):
        np.random.seed(int(time.time()))
        space = total_len - len(self.message)
        n = np.random.randint(0, space+1)

        i = np.random.randint(0, len(self.charSet), size=n)
        a = [self.charSet[k] for k in i]
        A = ''.join(a)

        i = np.random.randint(0, len(self.charSet), size=space-n)
        b = [self.charSet[k] for k in i]
        B = ''.join(b)

        s = ''.join([A, self.message, B])
        self.message = s
        return None


e = Enigma(seed=31415, nRotors='rand', evenBounce=True, charSet='default')
e.get_input()
code = e.encode()
print('\n\n')
print(code)
print('\n\n')

f = Enigma(seed=31415, nRotors='rand', evenBounce=True, charSet='default')
f.message = code
code = f.encode()
print(code)
