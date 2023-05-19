import socket
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class ChatServer:
    def __init__(self):
        self.server_address = ('localhost', 12345)
        self.server_socket = None
        self.clients = {}
        self.messages = []

        self.root = tk.Tk()
        self.root.title("Serwer")
        self.root.configure(bg="#202020")

        self.messages_frame = tk.Frame(self.root, bg="#202020")
        self.messages_frame.pack(pady=10)

        self.messages_label = tk.Label(self.messages_frame, text="Wiadomości:", bg="#202020", fg="white")
        self.messages_label.pack(side=tk.LEFT)

        self.messages_text = tk.Text(self.messages_frame, height=10, width=50, bg="#202020", fg="white")
        self.messages_text.pack()

        self.style = ttk.Style()
        self.style.configure("TLabel", foreground="white", background="#202020")
        self.style.configure("TText", foreground="white", background="#202020")

        self.start_button = tk.Button(self.root, text="Start", command=self.start_server, bg="#303030", fg="white")
        self.start_button.pack(pady=10)

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(self.server_address)
        self.server_socket.listen(5)

        self.start_button.configure(state=tk.DISABLED)
        self.messages_text.insert(tk.END, "Serwer nasłuchuje na {}:{}".format(*self.server_address) + "\n")

        threading.Thread(target=self.accept_clients).start()

        self.root.mainloop()

    def accept_clients(self):
        while True:
            client_socket, client_address = self.server_socket.accept()
            client_name = client_socket.recv(1024).decode('utf-8')
            self.clients[client_socket] = client_name

            threading.Thread(target=self.handle_client, args=(client_socket, client_name)).start()

    def handle_client(self, client_socket, client_name):
        self.broadcast_message("Serwer", "{} dołączył do czatu.".format(client_name))

        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if message:
                    if message.startswith("/nick"):
                        new_name = message.split("/nick")[1].strip()
                        self.change_nickname(client_socket, client_name, new_name)
                    else:
                        self.broadcast_message(client_name, message)
            except Exception as e:
                print("Błąd podczas odbierania wiadomości od {}: {}".format(client_name, str(e)))
                del self.clients[client_socket]
                self.broadcast_message("Serwer", "{} opuścił czat.".format(client_name))
                break

    def change_nickname(self, client_socket, old_name, new_name):
        if new_name:
            self.clients[client_socket] = new_name
            self.broadcast_message("Serwer", "{} zmienił nick na {}.".format(old_name, new_name))

    def broadcast_message(self, sender_name, message):
        full_message = "{}: {}".format(sender_name, message)
        self.messages.append(full_message)
        self.messages_text.delete(1.0, tk.END)
        for msg in self.messages:
            self.messages_text.insert(tk.END, msg + "\n")
        for client_socket in self.clients.keys():
            try:
                client_socket.send(full_message.encode('utf-8'))
            except Exception as e:
                print("Błąd podczas wysyłania wiadomości do {}: {}".format(self.clients[client_socket], str(e)))
                del self.clients[client_socket]

class ChatClient:
    def __init__(self):
        self.server_address = ('localhost', 12345)
        self.client_socket = None

        self.root = tk.Tk()
        self.root.title("Klient")
        self.root.configure(bg="#202020")

        self.nickname_frame = tk.Frame(self.root, bg="#202020")
        self.nickname_frame.pack(pady=10)

        self.nickname_label = tk.Label(self.nickname_frame, text="Nick:", bg="#202020", fg="white")
        self.nickname_label.pack(side=tk.LEFT)

        self.nickname_entry = tk.Entry(self.nickname_frame)
        self.nickname_entry.pack(side=tk.LEFT, padx=10)

        self.server_frame = tk.Frame(self.root, bg="#202020")
        self.server_frame.pack(pady=10)

        self.server_label = tk.Label(self.server_frame, text="Serwer:", bg="#202020", fg="white")
        self.server_label.pack(side=tk.LEFT)

        self.server_entry = tk.Entry(self.server_frame)
        self.server_entry.pack(side=tk.LEFT, padx=10)

        self.connect_button = tk.Button(self.root, text="Połącz", command=self.connect_to_server, bg="#303030", fg="white")
        self.connect_button.pack(pady=10)

        self.messages_frame = tk.Frame(self.root, bg="#202020")
        self.messages_frame.pack(pady=10)

        self.messages_label = tk.Label(self.messages_frame, text="Wiadomości:", bg="#202020", fg="white")
        self.messages_label.pack(side=tk.LEFT)

        self.messages_text = tk.Text(self.messages_frame, height=10, width=50, bg="#202020", fg="white")
        self.messages_text.pack()

        self.message_frame = tk.Frame(self.root, bg="#202020")
        self.message_frame.pack(pady=10)

        self.message_label = tk.Label(self.message_frame, text="Wiadomość:", bg="#202020", fg="white")
        self.message_label.pack(side=tk.LEFT)

        self.message_entry = tk.Entry(self.message_frame)
        self.message_entry.pack(side=tk.LEFT, padx=10)

        self.send_button = tk.Button(self.root, text="Wyślij", command=self.send_message, bg="#303030", fg="white")
        self.send_button.pack(pady=10)

        self.style = ttk.Style()
        self.style.configure("TLabel", foreground="white", background="#202020")
        self.style.configure("TText", foreground="white", background="#202020")
        self.style.configure("TButton", foreground="white", background="#303030")
        self.style.configure("TEntry", foreground="black", background="white")

    def connect_to_server(self):
        nickname = self.nickname_entry.get().strip()
        server_address = self.server_entry.get().strip()

        if nickname and server_address:
            self.server_address = (server_address, 12345)
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect(self.server_address)
            self.client_socket.send(nickname.encode('utf-8'))

            self.nickname_entry.configure(state=tk.DISABLED)
            self.server_entry.configure(state=tk.DISABLED)
            self.connect_button.configure(state=tk.DISABLED)
            self.message_entry.configure(state=tk.NORMAL)
            self.send_button.configure(state=tk.NORMAL)

            threading.Thread(target=self.receive_messages).start()
        else:
            messagebox.showwarning("Błąd", "Wprowadź poprawny nick i adres serwera.")

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message:
                    self.messages_text.insert(tk.END, message + "\n")
                    self.messages_text.see(tk.END)
            except Exception as e:
                print("Błąd podczas odbierania wiadomości:", str(e))
                break

    def send_message(self):
        message = self.message_entry.get()
        if message:
            try:
                self.client_socket.send(message.encode('utf-8'))
                self.message_entry.delete(0, tk.END)
            except Exception as e:
                print("Błąd podczas wysyłania wiadomości:", str(e))
        else:
            messagebox.showwarning("Błąd", "Wprowadź wiadomość")

if __name__ == "__main__":
    server = ChatServer()
    server_thread = threading.Thread(target=server.start_server)
    server_thread.daemon = True
    server_thread.start()

    client = ChatClient()
    client.root.mainloop()
