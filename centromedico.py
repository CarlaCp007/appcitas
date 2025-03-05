import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from tkcalendar import Calendar
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os

class AppCitasMedicas:
    def __init__(self, root):
        self.root = root
        self.root.title("Centro Médico")
        self.root.title("Salud a tu alcance")
        self.root.geometry("1000x650")
        self.root.resizable(False, False)
        self.root.configure(bg="#cacfd2")

        # Conexión a SQLite3
        self.conn = sqlite3.connect("citas.db")
        self.crear_tablas()

        #Diccionario de especialidades y doctores
        self.doctor_especialidades = {
            "Pediatría": ["Dr. Alejandro Pérez", "Dra. María Jose López"],
            "Medicina General": ["Dr. David Cardenas","Dra. Selena Murillo"],
            "Psicología": ["Dra. Luisa Narvaez", "Dra. Sofia Lara"],
            "Obstetricia": ["Dra. Maria Ruiz", "Dra. Lara Velez"],
            "Pediatría": ["Dr. Roberto García", "Dra. Sofia Rodríguez"],
            "Odontología": ["Dr. Luis Guerrero", "Dr. Miguel Parra"],
            "Traumatología": ["Dra. Luna Vargas"],
            "Dermatología": ["Dr. Raúl Ruiz",]
            }

        #Variables
        self.usuario_actual = None

        #Frames
        self.frame_inicio = tk.Frame(root, bg="#cacfd2")
        self.frame_registro = tk.Frame(root, bg="#cacfd2")
        self.frame_citas_paciente = tk.Frame(root, bg="#cacfd2")
        self.frame_admin = tk.Frame(root, bg="#cacfd2")

        #Configurar estilos de botones
        self.configurar_estilos_botones()

        #Inicializar interfaces
        self.inicializar_inicio()
        self.inicializar_registro()
        self.inicializar_citas_paciente()
        self.inicializar_admin()

        # Mostrar pantalla inicial
        self.mostrar_inicio()

    def configurar_estilos_botones(self):
        #Estilo para botones verdes (acciones generales)
        estilo = ttk.Style()
        estilo.configure("Green.TButton", font=("Helvetica", 11), padding=10, background="#4CAF50", foreground="black")
        estilo.map("Green.TButton", background=[('active', '#45a049')])

        #Estilo para botones rojos (Eliminar Cita)
        estilo.configure("Red.TButton", font=("Helvetica", 11), padding=10, background="#f44336", foreground="white")
        estilo.map("Red.TButton", background=[('active', '#da190b')])

        #Estilo para botones naranjas (Descargar el PDF)
        estilo.configure("Orange.TButton", font=("Helvetica", 11), padding=10, background="#ff9800", foreground="white")
        estilo.map("Orange.TButton", background=[('active', '#f57c00')])
#creacion de tablas
    def crear_tablas(self):
        cursor = self.conn.cursor()
        # Tabla de usuarios
        cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
            usuario TEXT PRIMARY KEY,
            nombre TEXT,
            apellido TEXT,
            edad TEXT,
            correo TEXT,
            password TEXT,
            es_admin INTEGER DEFAULT 0
        )''')

        #Tabla de citas
        cursor.execute('''CREATE TABLE IF NOT EXISTS citas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente TEXT,
            especialidad TEXT,
            doctor TEXT,
            fecha TEXT,
            hora TEXT,
            FOREIGN KEY (paciente) REFERENCES usuarios(usuario)
        )''')

        #Crear admin por defecto si no existe
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE usuario = 'adminboris'")
        if cursor.fetchone()[0] == 0:
            cursor.execute('''INSERT INTO usuarios (usuario, nombre, apellido, edad, correo, password, es_admin)
                            VALUES ( ?, ?, ?, ?, ?, ?, ?)''',
                          ("admin", "Admin", "Carla", "30", "admin@hospital.com", "admin123", 1))
        self.conn.commit()

    def limpiar_pantalla(self):
        for frame in [self.frame_inicio, self.frame_registro, self.frame_citas_paciente, self.frame_admin]:
            frame.pack_forget()

    # PANTALLA DE INICIO
    def inicializar_inicio(self):
        # Estilo
        estilo = ttk.Style()
        estilo.configure("TButton", font=("Helvetica", 11), padding=10)

        # Título
        tk.Label(self.frame_inicio, text="Centro Médico", font=("Helvetica", 24, "bold"), 
                bg="#cacfd2", fg="#000000").pack(pady=20)
        tk.Label(self.frame_inicio, text="Salud a tu alcance\n \nSistema de Gestión de Citas Médicas", font=("Helvetica", 14), 
                bg="#cacfd2", fg="#000000").pack()

        # Frame login
        frame_login = tk.Frame(self.frame_inicio, bg="#ffffff", padx=20, pady=20, relief=tk.RAISED, bd=2)
        frame_login.pack(pady=30)

        tk.Label(frame_login, text="Usuario:", font=("Helvetica", 12), bg="#ffffff", fg="#000000").grid(row=0, column=0, padx=10, pady=10)
        self.entry_usuario = tk.Entry(frame_login, width=30, font=("Helvetica", 11))
        self.entry_usuario.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(frame_login, text="Contraseña:", font=("Helvetica", 12), bg="#ffffff", fg="#000000").grid(row=1, column=0, padx=10, pady=10)
        self.entry_password = tk.Entry(frame_login, width=30, show="*", font=("Helvetica", 11))
        self.entry_password.grid(row=1, column=1, padx=10, pady=10)

        # Botones
        frame_botones = tk.Frame(self.frame_inicio, bg="#cacfd2")
        frame_botones.pack(pady=20)

        ttk.Button(frame_botones, text="Paciente", style="Green.TButton", command=self.login_paciente).grid(row=0, column=0, padx=10)
        ttk.Button(frame_botones, text="Administrador", style="Green.TButton", command=self.login_admin).grid(row=0, column=1, padx=10)
        ttk.Button(frame_botones, text="Registrarse", style="Green.TButton", command=self.mostrar_registro).grid(row=1, column=0, padx=10, pady=10)
        ttk.Button(frame_botones, text="Olvidé mi contraseña", style="Green.TButton", command=self.mostrar_recuperar_contraseña).grid(row=1, column=1, padx=10, pady=10)

    def login_paciente(self):
        usuario = self.entry_usuario.get()
        password = self.entry_password.get()
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE usuario=? AND password=? AND es_admin=0", (usuario, password))
        if cursor.fetchone():
            self.usuario_actual = usuario
            self.mostrar_citas_paciente()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")

    def login_admin(self):
        usuario = self.entry_usuario.get()
        password = self.entry_password.get()
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE usuario=? AND password=? AND es_admin=1", (usuario, password))
        if cursor.fetchone():
            self.usuario_actual = usuario
            self.mostrar_admin()
        else:
            messagebox.showerror("Error", "Credenciales de administrador incorrectas")

    def mostrar_inicio(self):
        self.limpiar_pantalla()
        self.frame_inicio.pack(fill="both", expand=True)
        self.entry_usuario.delete(0, tk.END)
        self.entry_password.delete(0, tk.END)

    # === RECUPERAR CONTRASEÑA ===
    def mostrar_recuperar_contraseña(self):
        # Crear una ventana emergente
        ventana_recuperar = tk.Toplevel(self.root)
        ventana_recuperar.title("Recuperar Contraseña")
        ventana_recuperar.geometry("400x300")
        ventana_recuperar.resizable(False, False)
        ventana_recuperar.configure(bg="#cacfd2")

        # Frame para el formulario
        frame_recuperar = tk.Frame(ventana_recuperar, bg="#ffffff", padx=20, pady=20, relief=tk.RAISED, bd=2)
        frame_recuperar.pack(pady=20)

        # Campos
        tk.Label(frame_recuperar, text="Usuario:", font=("Helvetica", 12), bg="#ffffff", fg="#000000").grid(row=0, column=0, padx=10, pady=10)
        self.entry_recuperar_usuario = tk.Entry(frame_recuperar, width=30, font=("Helvetica", 11))
        self.entry_recuperar_usuario.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(frame_recuperar, text="Correo:", font=("Helvetica", 12), bg="#ffffff", fg="#000000").grid(row=1, column=0, padx=10, pady=10)
        self.entry_recuperar_correo = tk.Entry(frame_recuperar, width=30, font=("Helvetica", 11))
        self.entry_recuperar_correo.grid(row=1, column=1, padx=10, pady=10)

        # Botones
        frame_botones_recuperar = tk.Frame(ventana_recuperar, bg="#cacfd2")
        frame_botones_recuperar.pack(pady=10)

        ttk.Button(frame_botones_recuperar, text="Recuperar", style="Green.TButton", command=self.recuperar_contraseña).grid(row=0, column=0, padx=10)
        ttk.Button(frame_botones_recuperar, text="Cancelar", style="Green.TButton", command=ventana_recuperar.destroy).grid(row=0, column=1, padx=10)

    def recuperar_contraseña(self):
        usuario = self.entry_recuperar_usuario.get()
        correo = self.entry_recuperar_correo.get()

        if not usuario or not correo:
            messagebox.showerror("Error", "Por favor, ingrese usuario y correo")
            return

        cursor = self.conn.cursor()
        cursor.execute("SELECT password FROM usuarios WHERE usuario=? AND correo=?", (usuario, correo))
        resultado = cursor.fetchone()

        if resultado:
            contraseña = resultado[0]
            messagebox.showinfo("Contraseña Recuperada", f"Su contraseña es: {contraseña}\nRecomendamos cambiarla después de iniciar sesión.")
            self.entry_recuperar_usuario.delete(0, tk.END)
            self.entry_recuperar_correo.delete(0, tk.END)
            self.entry_recuperar_usuario.winfo_toplevel().destroy()  # Cerrar la ventana
        else:
            messagebox.showerror("Error", "Usuario o correo incorrectos")

    # === PANTALLA DE REGISTRO ===
    def inicializar_registro(self):
        tk.Label(self.frame_registro, text="Registro de Paciente", font=("Helvetica", 20, "bold"), 
                bg="#cacfd2", fg="#000000").pack(pady=20)

        frame_form = tk.Frame(self.frame_registro, bg="#ffffff", padx=20, pady=20, relief=tk.RAISED, bd=2)
        frame_form.pack(pady=10)

        campos = [
            ("Nombre:", "entry_reg_nombre"),
            ("Apellido:", "entry_reg_apellido"),
            ("Edad:", "entry_reg_edad"),
            ("Correo:", "entry_reg_correo"),
            ("Usuario:", "entry_reg_usuario"),
            ("Contraseña:", "entry_reg_password")
        ]

        for i, (label, attr) in enumerate(campos):
            tk.Label(frame_form, text=label, font=("Helvetica", 12), bg="#ffffff", fg="#000000").grid(row=i, column=0, padx=10, pady=10)
            entry = tk.Entry(frame_form, width=40, font=("Helvetica", 11))
            entry.grid(row=i, column=1, padx=10, pady=10)
            if attr == "entry_reg_password":
                entry.config(show="*")
            setattr(self, attr, entry)

        frame_botones = tk.Frame(self.frame_registro, bg="#cacfd2")
        frame_botones.pack(pady=20)

        ttk.Button(frame_botones, text="Registrar", style="Green.TButton", command=self.registrar_usuario).grid(row=0, column=0, padx=10)
        ttk.Button(frame_botones, text="Volver", style="Green.TButton", command=self.mostrar_inicio).grid(row=0, column=1, padx=10)

    def registrar_usuario(self):
        datos = [
            self.entry_reg_usuario.get(),
            self.entry_reg_nombre.get(),
            self.entry_reg_apellido.get(),
            self.entry_reg_edad.get(),
            self.entry_reg_correo.get(),
            self.entry_reg_password.get(),
            0  # es_admin
        ]

        if not all(datos[:-1]):
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return

        cursor = self.conn.cursor()
        try:
            cursor.execute('''INSERT INTO usuarios (usuario, nombre, apellido, edad, correo, password, es_admin)
                            VALUES (?, ?, ?, ?, ?, ?, ?)''', datos)
            self.conn.commit()
            messagebox.showinfo("Éxito", "Usuario registrado correctamente")
            self.usuario_actual = datos[0]
            self.mostrar_citas_paciente()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "El nombre de usuario ya existe")

    def mostrar_registro(self):
        self.limpiar_pantalla()
        for attr in ["entry_reg_nombre", "entry_reg_apellido", "entry_reg_edad",
                    "entry_reg_correo", "entry_reg_usuario", "entry_reg_password"]:
            if hasattr(self, attr):
                getattr(self, attr).delete(0, tk.END)
        self.frame_registro.pack(fill="both", expand=True)

    # === PANTALLA DE CITAS PACIENTE ===
    def inicializar_citas_paciente(self):
        self.label_bienvenida = tk.Label(self.frame_citas_paciente, text="", font=("Helvetica", 16, "bold"),
                                       bg="#e6f3ff", fg="#000000")
        self.label_bienvenida.pack(pady=15)

        frame_main = tk.Frame(self.frame_citas_paciente, bg="#e6f3ff")
        frame_main.pack(fill="both", expand=True, padx=20, pady=10)

        # Agendar cita
        frame_agendar = tk.LabelFrame(frame_main, text="Agendar Nueva Cita", font=("Helvetica", 12), 
                                    bg="#ffffff", padx=10, pady=10)
        frame_agendar.grid(row=0, column=0, padx=10, sticky="n")

        tk.Label(frame_agendar, text="Especialidad:", bg="#ffffff", fg="#000000").grid(row=0, column=0, pady=5)
        self.combo_especialidad = ttk.Combobox(frame_agendar, width=25, state="readonly")
        self.combo_especialidad.grid(row=0, column=1, pady=5, padx=5)
        self.combo_especialidad["values"] = list(self.doctor_especialidades.keys())
        self.combo_especialidad.bind("<<ComboboxSelected>>", self.actualizar_doctores)

        tk.Label(frame_agendar, text="Doctor:", bg="#ffffff", fg="#000000").grid(row=1, column=0, pady=5)
        self.combo_doctor = ttk.Combobox(frame_agendar, width=25, state="readonly")
        self.combo_doctor.grid(row=1, column=1, pady=5, padx=5)

        tk.Label(frame_agendar, text="Fecha:", bg="#ffffff", fg="#000000").grid(row=2, column=0, pady=5)
        self.calendario = Calendar(frame_agendar, selectmode="day", date_pattern="yyyy-mm-dd")
        self.calendario.grid(row=2, column=1, pady=5, padx=5)

        tk.Label(frame_agendar, text="Hora:", bg="#ffffff", fg="#000000").grid(row=3, column=0, pady=5)
        self.combo_hora = ttk.Combobox(frame_agendar, width=25, state="readonly")
        self.combo_hora.grid(row=3, column=1, pady=5, padx=5)
        self.combo_hora["values"] = [f"{h:02d}:00" for h in range(8, 18)]

        ttk.Button(frame_agendar, text="Agendar Cita", style="Green.TButton", command=self.agendar_cita).grid(row=4, column=0, columnspan=2, pady=15)

        # Mis citas
        frame_mis_citas = tk.LabelFrame(frame_main, text="Mis Citas", font=("Helvetica", 12), bg="#ffffff", padx=10, pady=10)
        frame_mis_citas.grid(row=0, column=1, padx=10, sticky="n")

        self.tree_citas = ttk.Treeview(frame_mis_citas, columns=("fecha", "hora", "especialidad", "doctor", "id"), show="headings")
        self.tree_citas.heading("fecha", text="Fecha")
        self.tree_citas.heading("hora", text="Hora")
        self.tree_citas.heading("especialidad", text="Especialidad")
        self.tree_citas.heading("doctor", text="Doctor")
        self.tree_citas.heading("id", text="ID")
        self.tree_citas.column("fecha", width=100)
        self.tree_citas.column("hora", width=70)
        self.tree_citas.column("especialidad", width=120)
        self.tree_citas.column("doctor", width=150)
        self.tree_citas.column("id", width=0, stretch=False)
        self.tree_citas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(frame_mis_citas, orient=tk.VERTICAL, command=self.tree_citas.yview)
        self.tree_citas.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        frame_acciones = tk.Frame(frame_mis_citas, bg="#ffffff")
        frame_acciones.pack(pady=10)
        ttk.Button(frame_acciones, text="Cancelar", style="Green.TButton", command=self.cancelar_cita_paciente).grid(row=0, column=0, padx=5)
        ttk.Button(frame_acciones, text="Reagendar", style="Green.TButton", command=self.mostrar_reagendar).grid(row=0, column=1, padx=5)
        ttk.Button(self.frame_citas_paciente, text="Cerrar Sesión", style="Green.TButton", command=self.mostrar_inicio).pack(pady=15)

        # Frame reagendar
        self.frame_reagendar = tk.LabelFrame(self.frame_citas_paciente, text="Reagendar Cita", font=("Helvetica", 12), bg="#ffffff", padx=10, pady=10)
        tk.Label(self.frame_reagendar, text="Nueva fecha:", bg="#ffffff", fg="#000000").grid(row=0, column=0, pady=5)
        self.calendario_reagendar = Calendar(self.frame_reagendar, selectmode="day", date_pattern="yyyy-mm-dd")
        self.calendario_reagendar.grid(row=0, column=1, pady=5, padx=5)
        tk.Label(self.frame_reagendar, text="Nueva hora:", bg="#ffffff", fg="#000000").grid(row=1, column=0, pady=5)
        self.combo_hora_reagendar = ttk.Combobox(self.frame_reagendar, width=25, state="readonly")
        self.combo_hora_reagendar.grid(row=1, column=1, pady=5, padx=5)
        self.combo_hora_reagendar["values"] = [f"{h:02d}:00" for h in range(8, 18)]
        ttk.Button(self.frame_reagendar, text="Confirmar", style="Green.TButton", command=self.reagendar_cita).grid(row=2, column=0, pady=10, padx=5)
        ttk.Button(self.frame_reagendar, text="Cancelar", style="Green.TButton", command=lambda: self.frame_reagendar.place_forget()).grid(row=2, column=1, pady=10, padx=5)

    def actualizar_doctores(self, event=None):
        especialidad = self.combo_especialidad.get()
        if especialidad in self.doctor_especialidades:
            self.combo_doctor["values"] = self.doctor_especialidades[especialidad]
            self.combo_doctor.current(0)

    def agendar_cita(self):
        if not all([self.combo_especialidad.get(), self.combo_doctor.get(), self.calendario.get_date(), self.combo_hora.get()]):
            messagebox.showerror("Error", "Debe completar todos los campos")
            return

        cursor = self.conn.cursor()
        doctor = self.combo_doctor.get()
        fecha = self.calendario.get_date()
        hora = self.combo_hora.get()
        
        # Validar si la cita ya existe
        cursor.execute("SELECT * FROM citas WHERE doctor=? AND fecha=? AND hora=?", (doctor, fecha, hora))
    
        if cursor.fetchone():  # Si hay un resultado, significa que la cita ya existe
            messagebox.showerror("Error", "Ya existe una cita para la fecha y hora seleccionada")
            return  # Salir de la función

        # Insertar la nueva cita si no existe una duplicada
        datos = (self.usuario_actual, self.combo_especialidad.get(), doctor, fecha, hora)
        cursor.execute("INSERT INTO citas (paciente, especialidad, doctor, fecha, hora) VALUES (?, ?, ?, ?, ?)", datos)
        
        self.conn.commit()  # Guardar cambios
        messagebox.showinfo("Éxito", "Cita agendada correctamente")
        self.actualizar_lista_citas()  # Refrescar la lista de citas

    def cancelar_cita_paciente(self):
        seleccionado = self.tree_citas.selection()
        if not seleccionado:
            messagebox.showerror("Error", "Debe seleccionar una cita")
            return

        id_cita = self.tree_citas.item(seleccionado)["values"][-1]
        if messagebox.askyesno("Confirmar", "¿Está seguro de cancelar esta cita?"):
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM citas WHERE id=?", (id_cita,))
            self.conn.commit()
            messagebox.showinfo("Éxito", "Cita cancelada correctamente")
            self.actualizar_lista_citas()

    def mostrar_reagendar(self):
        seleccionado = self.tree_citas.selection()
        if not seleccionado:
            messagebox.showerror("Error", "Debe seleccionar una cita")
            return
        self.cita_seleccionada = self.tree_citas.item(seleccionado)["values"][-1]
        self.frame_reagendar.place(relx=0.5, rely=0.5, anchor="center")

    def reagendar_cita(self):
        nueva_fecha = self.calendario_reagendar.get_date()
        nueva_hora = self.combo_hora_reagendar.get()
        if not nueva_fecha or not nueva_hora:
            messagebox.showerror("Error", "Debe seleccionar fecha y hora")
            return

        cursor = self.conn.cursor()
        cursor.execute("SELECT doctor FROM citas WHERE id=?", (self.cita_seleccionada,))
        doctor = cursor.fetchone()[0]
        
        # Verificar si ya existe una cita para el mismo doctor, nueva fecha y hora
        cursor.execute("SELECT * FROM citas WHERE doctor=? AND fecha=? AND hora=?", (doctor, nueva_fecha, nueva_hora))
        if cursor.fetchone() and cursor.fetchone()[0] != self.cita_seleccionada:
            messagebox.showerror("Error", "Ya existe una cita para este doctor en la fecha y hora seleccionada")
            return

        cursor.execute("UPDATE citas SET fecha=?, hora=? WHERE id=?", (nueva_fecha, nueva_hora, self.cita_seleccionada))
        self.conn.commit()
        messagebox.showinfo("Éxito", "Cita reagendada correctamente")
        self.frame_reagendar.place_forget()
        self.actualizar_lista_citas()

    def actualizar_lista_citas(self):
        for item in self.tree_citas.get_children():
            self.tree_citas.delete(item)
        cursor = self.conn.cursor()
        cursor.execute("SELECT fecha, hora, especialidad, doctor, id FROM citas WHERE paciente=?", (self.usuario_actual,))
        for row in cursor.fetchall():
            self.tree_citas.insert("", "end", values=row)

    def mostrar_citas_paciente(self):
        self.limpiar_pantalla()
        cursor = self.conn.cursor()
        cursor.execute("SELECT nombre FROM usuarios WHERE usuario=?", (self.usuario_actual,))
        nombre = cursor.fetchone()[0]
        self.label_bienvenida.config(text=f"Bienvenido/a, {nombre}")
        self.actualizar_lista_citas()
        self.frame_reagendar.place_forget()
        self.frame_citas_paciente.pack(fill="both", expand=True)

    # === PANTALLA DE ADMINISTRADOR ===
    def inicializar_admin(self):
        tk.Label(self.frame_admin, text="Panel de Administración", font=("Helvetica", 20, "bold"), 
                bg="#cacfd2", fg="#000000").pack(pady=15)

        frame_main = tk.Frame(self.frame_admin, bg="#cacfd2")
        frame_main.pack(fill="both", expand=True, padx=20, pady=10)

        frame_citas = tk.LabelFrame(frame_main, text="Todas las Citas", font=("Helvetica", 12), bg="#ffffff", padx=10, pady=10)
        frame_citas.pack(fill="both", expand=True)

        self.tree_admin_citas = ttk.Treeview(frame_citas, 
                                           columns=("id", "paciente", "fecha", "hora", "especialidad", "doctor"),
                                           show="headings")
        for col in ("ID", "Paciente", "Fecha", "Hora", "Especialidad", "Doctor"):
            self.tree_admin_citas.heading(col.lower(), text=col)
            self.tree_admin_citas.column(col.lower(), width=100 if col != "Paciente" else 150)
        self.tree_admin_citas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(frame_citas, orient=tk.VERTICAL, command=self.tree_admin_citas.yview)
        self.tree_admin_citas.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        frame_acciones = tk.Frame(self.frame_admin, bg="#cacfd2")
        frame_acciones.pack(pady=15)
        ttk.Button(frame_acciones, text="Eliminar", style="Red.TButton", command=self.eliminar_cita_admin).grid(row=0, column=0, padx=10)
        ttk.Button(frame_acciones, text="Reagendar", style="Green.TButton", command=self.mostrar_reagendar_admin).grid(row=0, column=1, padx=10)
        ttk.Button(frame_acciones, text="Nueva Cita", style="Green.TButton", command=self.mostrar_nueva_cita_admin).grid(row=0, column=2, padx=10)
        ttk.Button(self.frame_admin, text="Cerrar Sesión", style="Green.TButton", command=self.mostrar_inicio).pack(pady=15)

        # Frame reagendar
        self.frame_reagendar_admin = tk.LabelFrame(self.frame_admin, text="Reagendar Cita", font=("Helvetica", 12),
                                                 bg="#ffffff", padx=10, pady=10)
        tk.Label(self.frame_reagendar_admin, text="Nueva fecha:", bg="#ffffff", fg="#000000").grid(row=0, column=0, pady=5)
        self.calendario_reagendar_admin = Calendar(self.frame_reagendar_admin, selectmode="day", date_pattern="yyyy-mm-dd")
        self.calendario_reagendar_admin.grid(row=0, column=1, pady=5, padx=5)
        tk.Label(self.frame_reagendar_admin, text="Nueva hora:", bg="#ffffff", fg="#000000").grid(row=1, column=0, pady=5)
        self.combo_hora_reagendar_admin = ttk.Combobox(self.frame_reagendar_admin, width=25, state="readonly")
        self.combo_hora_reagendar_admin.grid(row=1, column=1, pady=5, padx=5)
        self.combo_hora_reagendar_admin["values"] = [f"{h:02d}:00" for h in range(8, 18)]
        ttk.Button(self.frame_reagendar_admin, text="Confirmar", style="Green.TButton", command=self.reagendar_cita_admin).grid(row=2, column=0, pady=10, padx=5)
        ttk.Button(self.frame_reagendar_admin, text="Cancelar", style="Green.TButton", command=lambda: self.frame_reagendar_admin.place_forget()).grid(row=2, column=1, pady=10, padx=5)

        # Frame nueva cita
        self.frame_nueva_cita_admin = tk.LabelFrame(self.frame_admin, text="Nueva Cita", font=("Helvetica", 12),
                                                  bg="#ffffff", padx=10, pady=10)
        tk.Label(self.frame_nueva_cita_admin, text="Paciente:", bg="#ffffff", fg="#000000").grid(row=0, column=0, pady=5)
        self.combo_paciente_admin = ttk.Combobox(self.frame_nueva_cita_admin, width=25, state="readonly")
        self.combo_paciente_admin.grid(row=0, column=1, pady=5, padx=5)
        tk.Label(self.frame_nueva_cita_admin, text="Especialidad:", bg="#ffffff", fg="#000000").grid(row=1, column=0, pady=5)
        self.combo_especialidad_admin = ttk.Combobox(self.frame_nueva_cita_admin, width=25, state="readonly")
        self.combo_especialidad_admin.grid(row=1, column=1, pady=5, padx=5)
        self.combo_especialidad_admin["values"] = list(self.doctor_especialidades.keys())
        self.combo_especialidad_admin.bind("<<ComboboxSelected>>", self.actualizar_doctores_admin)
        tk.Label(self.frame_nueva_cita_admin, text="Doctor:", bg="#ffffff", fg="#000000").grid(row=2, column=0, pady=5)
        self.combo_doctor_admin = ttk.Combobox(self.frame_nueva_cita_admin, width=25, state="readonly")
        self.combo_doctor_admin.grid(row=2, column=1, pady=5, padx=5)
        tk.Label(self.frame_nueva_cita_admin, text="Fecha:", bg="#ffffff", fg="#000000").grid(row=3, column=0, pady=5)
        self.calendario_admin = Calendar(self.frame_nueva_cita_admin, selectmode="day", date_pattern="yyyy-mm-dd")
        self.calendario_admin.grid(row=3, column=1, pady=5, padx=5)
        tk.Label(self.frame_nueva_cita_admin, text="Hora:", bg="#ffffff", fg="#000000").grid(row=4, column=0, pady=5)
        self.combo_hora_admin = ttk.Combobox(self.frame_nueva_cita_admin, width=25, state="readonly")
        self.combo_hora_admin.grid(row=4, column=1, pady=5, padx=5)
        self.combo_hora_admin["values"] = [f"{h:02d}:00" for h in range(8, 18)]
        ttk.Button(self.frame_nueva_cita_admin, text="Confirmar", style="Green.TButton", command=self.crear_cita_admin).grid(row=5, column=0, pady=10, padx=5)
        ttk.Button(self.frame_nueva_cita_admin, text="Cancelar", style="Green.TButton", command=lambda: self.frame_nueva_cita_admin.place_forget()).grid(row=5, column=1, pady=10, padx=5)

    def actualizar_doctores_admin(self, event=None):
        especialidad = self.combo_especialidad_admin.get()
        if especialidad in self.doctor_especialidades:
            self.combo_doctor_admin["values"] = self.doctor_especialidades[especialidad]
            self.combo_doctor_admin.current(0)

    def actualizar_lista_citas_admin(self):
        for item in self.tree_admin_citas.get_children():
            self.tree_admin_citas.delete(item)
        cursor = self.conn.cursor()
        cursor.execute("SELECT c.id, u.nombre || ' ' || u.apellido, c.fecha, c.hora, c.especialidad, c.doctor FROM citas c JOIN usuarios u ON c.paciente = u.usuario")
        for row in cursor.fetchall():
            self.tree_admin_citas.insert("", "end", values=row)

    def eliminar_cita_admin(self):
        seleccionado = self.tree_admin_citas.selection()
        if not seleccionado:
            messagebox.showerror("Error", "Debe seleccionar una cita")
            return
        id_cita = self.tree_admin_citas.item(seleccionado)["values"][0]
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar esta cita?"):
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM citas WHERE id=?", (id_cita,))
            self.conn.commit()
            messagebox.showinfo("Éxito", "Cita eliminada correctamente")
            self.actualizar_lista_citas_admin()

    def mostrar_reagendar_admin(self):
        seleccionado = self.tree_admin_citas.selection()
        if not seleccionado:
            messagebox.showerror("Error", "Debe seleccionar una cita")
            return
        self.cita_seleccionada_admin = self.tree_admin_citas.item(seleccionado)["values"][0]
        self.frame_reagendar_admin.place(relx=0.5, rely=0.5, anchor="center")

    def reagendar_cita_admin(self):
        nueva_fecha = self.calendario_reagendar_admin.get_date()
        nueva_hora = self.combo_hora_reagendar_admin.get()
        if not nueva_fecha or not nueva_hora:
            messagebox.showerror("Error", "Debe seleccionar fecha y hora")
            return

        cursor = self.conn.cursor()
        cursor.execute("SELECT doctor FROM citas WHERE id=?", (self.cita_seleccionada_admin,))
        doctor = cursor.fetchone()[0]
        
        # Verificar si ya existe una cita para el mismo doctor nueva fecha y hora
        cursor.execute("SELECT * FROM citas WHERE doctor=? AND fecha=? AND hora=?", (doctor, nueva_fecha, nueva_hora))
        if cursor.fetchone() and cursor.fetchone()[0] != self.cita_seleccionada_admin:
            messagebox.showerror("Error", "Ya existe una cita para este doctor en la fecha y hora seleccionada")
            return

        cursor.execute("UPDATE citas SET fecha=?, hora=? WHERE id=?", (nueva_fecha, nueva_hora, self.cita_seleccionada_admin))
        self.conn.commit()
        messagebox.showinfo("Éxito", "Cita reagendada correctamente")
        self.frame_reagendar_admin.place_forget()
        self.actualizar_lista_citas_admin()

    def mostrar_nueva_cita_admin(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT nombre || ' ' || apellido || ' (' || usuario || ')' FROM usuarios WHERE es_admin=0")
        self.combo_paciente_admin["values"] = [row[0] for row in cursor.fetchall()]
        self.frame_nueva_cita_admin.place(relx=0.5, rely=0.5, anchor="center")

    def crear_cita_admin(self):
        if not all([self.combo_paciente_admin.get(), self.combo_especialidad_admin.get(), self.combo_doctor_admin.get(),
                   self.calendario_admin.get_date(), self.combo_hora_admin.get()]):
            messagebox.showerror("Error", "Debe completar todos los campos")
            return

        username = self.combo_paciente_admin.get().split("(")[-1].replace(")", "")
        doctor = self.combo_doctor_admin.get()
        fecha = self.calendario_admin.get_date()
        hora = self.combo_hora_admin.get()
        
        # Verificar si ya existe una cita para el mismo doctor, fecha y hora
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM citas WHERE doctor=? AND fecha=? AND hora=?", (doctor, fecha, hora))
        if cursor.fetchone():
            messagebox.showerror("Error", "Ya existe una cita para este doctor en la fecha y hora seleccionada")
            return

        datos = (username, self.combo_especialidad_admin.get(), doctor, fecha, hora)
        cursor.execute("INSERT INTO citas (paciente, especialidad, doctor, fecha, hora) VALUES (?, ?, ?, ?, ?)", datos)
        self.conn.commit()
        messagebox.showinfo("Éxito", "Cita creada correctamente")
        self.frame_nueva_cita_admin.place_forget()
        self.actualizar_lista_citas_admin()
    #mostrar por pantalla de administrador
    def mostrar_admin(self):
        self.limpiar_pantalla()
        self.actualizar_lista_citas_admin()
        self.frame_reagendar_admin.place_forget()
        self.frame_nueva_cita_admin.place_forget()
        self.frame_admin.pack(fill="both", expand=True)

# Funcion principal
def main():
    root = tk.Tk()
    app = AppCitasMedicas(root)
    root.mainloop()

if __name__ == "__main__":
    main()