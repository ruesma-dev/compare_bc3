# gui_tkinter.py
import threading
import subprocess
import os
import sys
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

# Importa tu controlador y tus settings
from interface_adapters.controllers.compare_controller import run as run_compare
from config import settings

class CompareApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Comparador BC3")
        self.geometry("700x450")
        self.resizable(False, False)

        # ---- Versión en esquina ----
        version_label = tk.Label(
            self,
            text=f"v{settings.APP_VERSION}",
            font=("Segoe UI", 8)
        )
        version_label.place(x=690, y=440, anchor="se")

        # ---- Rutas ----
        tk.Label(self, text="Presupuesto 1 (.bc3):").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.bc3_1_var = tk.StringVar()
        tk.Entry(self, textvariable=self.bc3_1_var, width=60).grid(row=0, column=1, padx=10)
        tk.Button(self, text="Examinar…", command=self.browse_bc3_1).grid(row=0, column=2, padx=10)

        tk.Label(self, text="Presupuesto 2 (.bc3):").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.bc3_2_var = tk.StringVar()
        tk.Entry(self, textvariable=self.bc3_2_var, width=60).grid(row=1, column=1, padx=10)
        tk.Button(self, text="Examinar…", command=self.browse_bc3_2).grid(row=1, column=2, padx=10)

        tk.Label(self, text="Carpeta de salida:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.outdir_var = tk.StringVar(value=str(Path("output").resolve()))
        tk.Entry(self, textvariable=self.outdir_var, width=60).grid(row=2, column=1, padx=10)
        tk.Button(self, text="Examinar…", command=self.browse_outdir).grid(row=2, column=2, padx=10)

        # ---- Botón grande ----
        self.btn_run = tk.Button(
            self, text="¡Comparar!", command=self.on_run,
            bg="green", fg="white", font=("Segoe UI", 14), width=15, height=2
        )
        self.btn_run.grid(row=3, column=0, columnspan=3, pady=15)

        # ---- Área de log ----
        self.log = scrolledtext.ScrolledText(self, state="disabled", width=80, height=12)
        self.log.grid(row=4, column=0, columnspan=3, padx=10, pady=5)

    def browse_bc3_1(self):
        path = filedialog.askopenfilename(filetypes=[("BC3 files", "*.bc3")])
        if path: self.bc3_1_var.set(path)

    def browse_bc3_2(self):
        path = filedialog.askopenfilename(filetypes=[("BC3 files", "*.bc3")])
        if path: self.bc3_2_var.set(path)

    def browse_outdir(self):
        path = filedialog.askdirectory()
        if path: self.outdir_var.set(path)

    def log_msg(self, msg: str):
        self.log.configure(state="normal")
        self.log.insert(tk.END, msg + "\n")
        self.log.see(tk.END)
        self.log.configure(state="disabled")

    def on_run(self):
        bc3_1 = Path(self.bc3_1_var.get())
        bc3_2 = Path(self.bc3_2_var.get())
        outdir = Path(self.outdir_var.get())

        if not bc3_1.exists() or not bc3_2.exists():
            messagebox.showerror("Error", "Debes seleccionar ambos archivos .bc3")
            return

        self.btn_run.config(state="disabled")
        self.log_msg(f"Lanzando comparación entre:\n  {bc3_1}\n  {bc3_2}\nSalida en: {outdir}")

        threading.Thread(target=self.worker, args=(bc3_1, bc3_2, outdir), daemon=True).start()

    def worker(self, bc3_1: Path, bc3_2: Path, outdir: Path):
        try:
            # Override de settings para escribir directamente en outdir
            mapping = [
                ("LONG_DESC_DIFF_XLSX_DEFAULT",   "comparativo_descripcion.xlsx", "Comparativo descripción"),
                ("PRICE_DIFF_XLSX_DEFAULT",       "comparativo_precio.xlsx",     "Comparativo precio"),
                ("QTY_DIFF_XLSX_DEFAULT",         "comparativo_medicion.xlsx",   "Comparativo medición"),
                ("IMP_DIFF_XLSX_DEFAULT",         "comparativo_importe.xlsx",    "Comparativo importe"),
                ("NEW_DEL_DIFF_XLSX_DEFAULT",     "nuevas_viejas_lineas.xlsx",   "Nuevas/Viejas líneas"),
            ]
            # Asegura carpeta outdir
            outdir.mkdir(parents=True, exist_ok=True)

            # Ajusta cada ruta en settings
            for attr, fname, _ in mapping:
                setattr(settings, attr, outdir / fname)

            # Ejecuta la comparación (usa los settings modificados)
            run_compare(bc3_1, bc3_2)

            # Ahora, loguea ruta de cada informe
            for attr, _, label in mapping:
                path = getattr(settings, attr)
                self.log_msg(f"{label} → {path.resolve()}")

            self.log_msg("✔ Comparación finalizada.")
            # Abre carpeta en Explorador
            subprocess.Popen(f'explorer "{outdir.resolve()}"')
        except Exception as e:
            self.log_msg(f"[ERROR] {e}")
        finally:
            self.btn_run.config(state="normal")


if __name__ == "__main__":
    app = CompareApp()
    app.mainloop()
