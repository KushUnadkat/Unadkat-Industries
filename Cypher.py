import socket
import threading

class EnigmaMachine:
    def __init__(self, rotors, reflector, plugboard_pairs, ring_settings, initial_positions):
        self.rotors = rotors
        self.reflector = reflector
        self.plugboard = self.create_plugboard(plugboard_pairs)
        self.ring_settings = ring_settings
        self.positions = initial_positions
        self.alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    def create_plugboard(self, pairs):
        plugboard = {letter: letter for letter in self.alphabet}
        for a, b in pairs:
            plugboard[a] = b
            plugboard[b] = a
        return plugboard

    def rotate_rotors(self):
        self.positions[0] = (self.positions[0] + 1) % 26
        if self.positions[0] == 0:
            self.positions[1] = (self.positions[1] + 1) % 26
            if self.positions[1] == 0:
                self.positions[2] = (self.positions[2] + 1) % 26

    def encipher_letter(self, letter):
        letter = self.plugboard[letter]
        index = self.alphabet.index(letter)
        for i, rotor in enumerate(self.rotors):
            index = (index + self.positions[i] - self.ring_settings[i]) % 26
            index = self.alphabet.index(rotor[index])
            index = (index - self.positions[i] + self.ring_settings[i]) % 26

        index = self.alphabet.index(self.reflector[index])

        for i, rotor in reversed(list(enumerate(self.rotors))):
            index = (index + self.positions[i] - self.ring_settings[i]) % 26
            index = rotor.index(self.alphabet[index])
            index = (index - self.positions[i] + self.ring_settings[i]) % 26

        letter = self.alphabet[index]
        letter = self.plugboard[letter]

        self.rotate_rotors()

        return letter

    def process_message(self, message):
        result = ''
        for letter in message:
            if letter in self.alphabet:
                result += self.encipher_letter(letter)
            else:
                result += letter
        return result

def receive_messages(client_socket, enigma, friend_name):
    while True:
        message = client_socket.recv(1024).decode('utf-8')
        if not message:
            break
        decoded_message = enigma.process_message(message)
        print(f"{friend_name}: {decoded_message}")
    client_socket.close()

def send_messages(client_socket, enigma):
    while True:
        message = input("You: ")
        encoded_message = enigma.process_message(message.upper())
        client_socket.send(encoded_message.encode('utf-8'))

def start_chat(host, port, friend_name):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))

    # Define the Enigma Machine configuration
    rotors = [
        'EKMFLGDQVZNTOWYHXUSPAIBRCJ',  # Rotor I
        'AJDKSIRUXBLHWTMCQGZNPYFVOE',  # Rotor II
        'BDFHJLCPRTXVZNYEIWGAKMUSQO'   # Rotor III
    ]
    reflector = 'YRUHQSLDPXNGOKMIEBFZCWVJAT'
    plugboard_pairs = [('A', 'M'), ('G', 'L'), ('E', 'T')]
    ring_settings = [1, 1, 1]
    initial_positions = [0, 0, 0]

    # Create an Enigma machine with the given configuration
    enigma = EnigmaMachine(rotors, reflector, plugboard_pairs, ring_settings, initial_positions)

    # Start receiving and sending messages in separate threads
    receive_thread = threading.Thread(target=receive_messages, args=(client, enigma, friend_name))
    send_thread = threading.Thread(target=send_messages, args=(client, enigma))

    receive_thread.start()
    send_thread.start()

    receive_thread.join()
    send_thread.join()

    client.close()

if __name__ == "__main__":
    host = input("Enter server IP: ")
    port = int(input("Enter server port: "))
    name = input("Enter your name: ")
    start_chat(host, port, name)
