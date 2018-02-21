import numpy as np
import time


class Enigma(object):
    """ Returns an instance of a randomly built Enigma(ish) Machine

    Parameters
    ----------

    seed: int
        Makes the RNG repeatable. Is used to generate identical machines.

    nRotors: int
        Sets the number of rotors. If None, the number of rotors is random.

    evenBounce: bool
        If there is an even number of characters, this options allows for two
        characters to be refelcted back to themselves (The inability to reflect
        down the input path was a huge secrity flaw in the original Enigma
        design). If there is an odd number of characters, there will always be
        one character that reflects back to itself.

    charSet: tuple
       Definition of allowable characters. If None, the default will be to use
       A,B,C...,X,Y,Z and a space (a total of 27 characters). Position in the
       tuple is very important: ('A', 'B', 'C') does not equal ('B', 'C', 'A')


    Attributes
    ----------
    reflector: numpy array
        Array of symetric indices. Ex: if reflect[n] = m then reflect[m] = n

    rotors: n-dim numpy array
        n dimension array of

    movement: numpy array

    offset: numpy array

    Returns
    -------
    """

    def __init__(self,
                 seed=0,
                 nRotors=None,
                 evenBounce=True,
                 charSet=None):
        ''' Build an instance of an Enigma(ish) Machine '''
        np.random.seed(seed)  # Set RNG

        self.charSet, self.nChar = self.__get_char_set(charSet)
        self.reflector = self.__build_reflector(evenBounce)
        self.rotors = self.__build_rotors(nRotors)
        self.movement = self.__set_movement()
        self.offset = np.random.randint(0, self.nChar, size=len(self.rotors))
        return None

    def __get_char_set(self, charSet):
        ''' Returns tuple of characters and the number of characters. '''
        if charSet is None:  # Use default character set
            self.charSet = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I',
                            'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R',
                            'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', ' ')
        else:  # Use user defined character set
            for char in charSet:
                if len(char) is not 1:
                    err = 'charSet Elements must contain single characters'
                    raise Exception(err)
                if type(char) is not str:
                    err = 'charSet Elements must be single character strings'
                    raise Exception(err)
            self.charSet = charSet
        return self.charSet, len(self.charSet)

    def __build_reflector(self, evenBounce):
        ''' Returns symetric reflector pattern
        Ex: if reflector[0] is 9, then reflector[9] is 0.
        '''
        # Determine the number of bounced characters
        nBounce = self.__bounce(evenBounce)

        # Generate a shuffled character index list
        r = np.arange(self.nChar)
        np.random.shuffle(r)

        # Create symetric indices by taking values off the end of the list
        ref = {}
        pairLen = int((self.nChar - nBounce) / 2)
        for i in range(pairLen):
            ref[r[i]] = r[(i+1)*-1]
            ref[r[(i+1)*-1]] = r[i]

        # If there are any bounced characters, set their value to their index
        for i in range(pairLen, pairLen+nBounce):
            ref[r[i]] = r[i]

        # Copy dictionary to numpy array
        for i in range(self.nChar):
            r[i] = ref[i]
        return r

    def __build_rotors(self, nRotors):
        ''' Returns a set of rotor configurations '''
        if nRotors is None:  # Use a random number of rotors
            nRotors = int(np.random.uniform(3, 50))
        else:
            nRotors = nRotors

        rotors = [np.arange(self.nChar) for i in range(nRotors)]
        for i in range(nRotors):
            np.random.shuffle(rotors[i])
        return rotors

    def __bounce(self, evenBounce):
        ''' Determines the number of "bounced" reflector positions '''
        if self.nChar % 2:  # If odd
            nBounce = 1
        else:  # If even
            if evenBounce:
                nBounce = 2
            else:
                nBounce = 0
        return nBounce

    def __set_movement(self):
        ''' Determines the rules for incrementing the rotors '''
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
        ''' Encodes plain text into cipher text '''
        message = ''
        for n in self.message:
            # Associate the character with its index position
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
        ''' Returns the forward output of a rotor for a specific character '''
        char = rotor[(char + self.offset[i]) % self.nChar]
        return char

    def reflect(self, char):
        ''' Returns the output of the reflector '''
        char = self.reflector[char]
        return char

    def feed_back(self, char, i, rotor):
        ''' Returns the reverse output of a rotor for a specific character '''
        char = np.where(rotor == char)
        return (int(char[0]) - self.offset[-(i+1)]) % self.nChar

    def turn_rotors(self):
        ''' Updates the rotor setting after each character input '''
        self.offset = (self.offset + self.movement) % self.nChar
        return None

    # -------------------------------------------------------------------------
    # ------------------ MESSAGE CONSTRUCTION ---------------------------------
    # -------------------------------------------------------------------------
    def get_input(self):
        ''' Requests message from user '''
        self.get_message()
        self.add_padding()
        self.rand_insert()
        print('Your message will be encoded as: \n{}'.format(self.message))
        return None

    def get_message(self, max_len=250):
        ''' Requests message from user '''
        self.max_len = max_len
        message = input("Enter your message: ")
        message_len = len(message)
        while message_len > max_len:
            print("Your message exceeds 250 characters.")
            message = input("Please reenter your message:")
            message_len = len(message)
        self.message = message.upper()
        return None

    def add_padding(self, nbuff=3, buffchar=' '):
        ''' Bookend message with unique character pattern '''
        self.message = ''.join([nbuff*buffchar, self.message, nbuff*buffchar])
        return None

    def rand_insert(self, total_len=256):
        ''' Randomly insert message into junk string '''
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


if __name__ == "__main__":
    e = Enigma(seed=31415, nRotors=None, evenBounce=True, charSet=None)
    e.get_input()
    code = e.encode()
    print('\n\n')
    print(code)
    print('\n\n')

    f = Enigma(seed=31415, nRotors=None, evenBounce=True, charSet=None)
    f.message = code
    code = f.encode()
    print(code)
