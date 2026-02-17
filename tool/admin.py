import json
import os
import shutil
import customtkinter as ctk
from PIL import Image
from tkinter import messagebox, filedialog

class MotorInventario:
    def __init__(self, img_folder, json_file):
        self.img_folder = img_folder
        self.json_file = json_file
        self.blacklist = ["logo.jpeg", "banner.jpeg", "logo.jpg", "banner.jpg"]
        # Abecedario para renombrado inteligente
        self.letras = list("abcdefghijklmnopqrstuvwxyz")

    def cargar_json(self):
        if os.path.exists(self.json_file):
            with open(self.json_file, 'r', encoding='utf-8') as f:
                try: return json.load(f)
                except: return []
        return []

    def guardar_json(self, datos):
        # Categorías unificadas con tu HTML
        categorias_validas = ["linia de marca", "linia fina", "linia media", "linia niño/a"]
        conteos = {cat: 0 for cat in categorias_validas}
        prefijos = {
            "linia de marca": "MARC", "linia fina": "FINA",
            "linia media": "MEDI", "linia niño/a": "NINO"
        }
        
        for item in datos:
            cat = item.get('cat', 'linia media').lower()
            if cat not in categorias_validas: cat = "linia media"
            
            conteos[cat] += 1
            item['id'] = f"{prefijos[cat]}-{str(conteos[cat]).zfill(3)}"
            item['cat'] = cat
            # Depuración de basura (eliminamos precio si existe)
            if 'precio' in item: del item['precio']

        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)

    def procesar_aspirado(self, carpeta_origen, inventario_actual):
        formatos = (".jpeg", ".jpg", ".png", ".webp")
        nombres_en_uso = {item['nombre'] for item in inventario_actual}
        
        archivos = [f for f in os.listdir(carpeta_origen) 
                   if f.lower().endswith(formatos) and f.lower() not in self.blacklist]
        
        for archivo in archivos:
            # Lógica de renombrado inteligente
            nombre_base = os.path.splitext(archivo)[0].lower().replace(" ", "_")
            
            if nombre_base not in nombres_en_uso:
                ruta_destino = os.path.join(self.img_folder, f"{nombre_base}.jpeg")
                try:
                    # Conversión y optimización
                    img = Image.open(os.path.join(carpeta_origen, archivo)).convert("RGB")
                    img.save(ruta_destino, "JPEG", quality=85)
                    
                    nuevo_item = {
                        "nombre": nombre_base,
                        "cat": "linia media",
                        "desc": "Nuevo ingreso - Cuidado profesional"
                    }
                    inventario_actual.append(nuevo_item)
                    nombres_en_uso.add(nombre_base)
                except Exception as e:
                    print(f"Error procesando {archivo}: {e}")
        return inventario_actual

class OptiAdmin(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Opticentro A&E - Panel Administrativo")
        self.geometry("1200x850")
        ctk.set_appearance_mode("dark")
        
        self.motor = MotorInventario("img/", "inventario.json")
        self.inventario = self.motor.cargar_json()
        self.item_seleccionado = None
        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # BARRA LATERAL (Pestañas por categoría)
        self.sidebar_frame = ctk.CTkFrame(self, width=350)
        self.sidebar_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar_frame, text="CATÁLOGO POR LÍNEAS", font=("Arial", 16, "bold")).pack(pady=10)
        
        self.tabview = ctk.CTkTabview(self.sidebar_frame, width=330, command=self.actualizar_lista)
        self.tabview.pack(expand=True, fill="both", padx=5, pady=5)
        
        self.mapa_tabs = {
            "linia de marca": self.tabview.add("Marca"),
            "linia fina": self.tabview.add("Fina"),
            "linia media": self.tabview.add("Media"),
            "linia niño/a": self.tabview.add("Niño/a")
        }
        
        self.scrolls = {cat: ctk.CTkScrollableFrame(self.mapa_tabs[cat], fg_color="transparent") for cat in self.mapa_tabs}
        for s in self.scrolls.values(): s.pack(expand=True, fill="both")

        # PANEL CENTRAL
        self.main = ctk.CTkScrollableFrame(self)
        self.main.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        f_btns = ctk.CTkFrame(self.main, fg_color="transparent")
        f_btns.pack(fill="x", pady=10)
        ctk.CTkButton(f_btns, text="IMPORTAR CARPETA", fg_color="#d35400", command=self.ui_aspirar).pack(side="left", padx=5)
        ctk.CTkButton(f_btns, text="LIMPIAR", fg_color="#27ae60", command=self.limpiar_vista).pack(side="left", padx=5)

        self.lbl_id = ctk.CTkLabel(self.main, text="SELECCIONE UN PRODUCTO", font=("Arial", 22, "bold"))
        self.lbl_id.pack(pady=10)

        self.img_view = ctk.CTkLabel(self.main, text="Vista Previa", width=500, height=400, fg_color="#222", corner_radius=15)
        self.img_view.pack(pady=15)

        self.combo_cat = ctk.CTkComboBox(self.main, values=list(self.mapa_tabs.keys()), width=300)
        self.combo_cat.pack(pady=10)

        self.txt_desc = ctk.CTkTextbox(self.main, height=100, width=500)
        self.txt_desc.pack(pady=10)

        f_acc = ctk.CTkFrame(self.main, fg_color="transparent")
        f_acc.pack(pady=20)
        ctk.CTkButton(f_acc, text="GUARDAR CAMBIOS", fg_color="#2980b9", command=self.ui_guardar, width=200).pack(side="left", padx=10)
        ctk.CTkButton(f_acc, text="ELIMINAR", fg_color="#c0392b", command=self.ui_borrar, width=200).pack(side="left", padx=10)
        
        self.actualizar_lista()

    def actualizar_lista(self):
        for scroll in self.scrolls.values():
            for w in scroll.winfo_children(): w.destroy()

        for i, p in enumerate(self.inventario):
            cat = p.get('cat', 'linia media').lower()
            if cat in self.scrolls:
                ctk.CTkButton(self.scrolls[cat], 
                             text=f"{p.get('id', 'N/A')} | {p['nombre'].upper()}",
                             anchor="w", fg_color="transparent" if self.item_seleccionado != i else "#333",
                             command=lambda idx=i: self.ui_cargar_item(idx)).pack(fill="x", pady=2)

    def ui_cargar_item(self, idx):
        self.item_seleccionado = idx
        p = self.inventario[idx]
        self.lbl_id.configure(text=f"ID: {p.get('id', 'SIN ID')}")
        
        path = f"img/{p['nombre']}.jpeg"
        if os.path.exists(path):
            img = Image.open(path).resize((500, 400))
            self.img_view.configure(image=ctk.CTkImage(img, size=(500, 400)), text="")
        
        self.combo_cat.set(p['cat'])
        self.txt_desc.delete("1.0", "end")
        self.txt_desc.insert("1.0", p.get('desc', ''))
        self.actualizar_lista()

    def ui_guardar(self):
        if self.item_seleccionado is not None:
            self.inventario[self.item_seleccionado]['cat'] = self.combo_cat.get()
            self.inventario[self.item_seleccionado]['desc'] = self.txt_desc.get("1.0", "end-1c")
            self.motor.guardar_json(self.inventario)
            self.actualizar_lista()
            messagebox.showinfo("Éxito", "Producto actualizado correctamente.")

    def ui_aspirar(self):
        folder = filedialog.askdirectory()
        if folder:
            self.inventario = self.motor.procesar_aspirado(folder, self.inventario)
            self.motor.guardar_json(self.inventario)
            self.actualizar_lista()
            messagebox.showinfo("Éxito", "Imágenes importadas y convertidas a .jpeg.")

    def ui_borrar(self):
        if self.item_seleccionado is not None:
            if messagebox.askyesno("Confirmar", "¿Eliminar imagen y registro permanentemente?"):
                self.motor.borrar_fisico(self.inventario[self.item_seleccionado]['nombre'])
                self.inventario.pop(self.item_seleccionado)
                self.motor.guardar_json(self.inventario)
                self.limpiar_vista()
                self.actualizar_lista()

    def limpiar_vista(self):
        self.item_seleccionado = None
        self.img_view.configure(image=None, text="Vista Previa")
        self.lbl_id.configure(text="SELECCIONE UN PRODUCTO")
        self.txt_desc.delete("1.0", "end")

if __name__ == "__main__":
    app = OptiAdmin()
    try:
        app.mainloop()
    except (KeyboardInterrupt, RuntimeError, Exception):
        print("\n✅ Panel cerrado correctamente. ¡Nos vemos, bro!")
    finally:
        try: app.destroy()
        except: pass