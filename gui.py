import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk


# -----------------------
# WINDOW
# -----------------------

root = tk.Tk()
root.title("Napoved vrednosti avtomobila")
root.geometry("1100x900")
root.configure(bg="#F8F8FA")


# -----------------------
# STYLE
# -----------------------

FONT = ("Helvetica Neue", 12)

style = ttk.Style()
style.theme_use("clam")

style.configure(
    "TLabel",
    background="#F8F8FA",
    font=FONT
)

style.configure(
    "TButton",
    font=("Helvetica Neue", 12),
    padding=10
)

style.configure(
    "TCombobox",
    padding=8
)


# -----------------------
# DATA
# -----------------------

cars = {
    "Citroen": {
        "Berlingo": {
            "1.5 BlueHDi": [100, 130],
            "1.2 PureTech": [110]
        }
    },

    "Renault": {
        "Clio": {
            "1.0 TCe": [90],
            "1.5 dCi": [115]
        }
    },

    "Volkswagen": {
        "Golf": {
            "1.5 TSI": [130, 150],
            "2.0 TDI": [115, 150]
        },

        "Passat Variant": {
            "2.0 TDI": [150, 200],
            "2.0 TSI": [220]
        }
    },

    "Kia": {
        "Ceed": {
            "1.0 T-GDI": [100],
            "1.5 T-GDI": [160]
        }
    },

    "Peugeot": {
        "208": {
            "1.2 PureTech": [100, 130],
            "e-208": [136]
        }
    }
}


# -----------------------
# VARIABLES
# -----------------------

znamka_var = tk.StringVar()
model_var = tk.StringVar()
engine_var = tk.StringVar()
hp_var = tk.StringVar()

owners_var = tk.StringVar()
km_var = tk.StringVar()

gearbox_var = tk.StringVar()
year_var = tk.StringVar()

image_path = tk.StringVar()


# -----------------------
# UPDATE
# -----------------------

def update_models(event=None):

    brand = znamka_var.get()

    model_dropdown["values"] = list(
        cars[brand].keys()
    )

    model_var.set("")
    engine_var.set("")
    hp_var.set("")

    engine_dropdown["values"] = []
    hp_dropdown["values"] = []


def update_engines(event=None):

    brand = znamka_var.get()
    model = model_var.get()

    engine_dropdown["values"] = list(
        cars[brand][model].keys()
    )

    engine_var.set("")
    hp_var.set("")

    hp_dropdown["values"] = []


def update_hp(event=None):

    brand = znamka_var.get()
    model = model_var.get()
    engine = engine_var.get()

    hp_dropdown["values"] = (
        cars[brand][model][engine]
    )

    hp_var.set("")


# -----------------------
# IMAGE
# -----------------------

preview = None


def upload_image():

    global preview

    path = filedialog.askopenfilename(
        filetypes=[
            ("Images", "*.jpg *.jpeg *.png")
        ]
    )

    if not path:
        return

    image_path.set(path)

    img = Image.open(path)

    img.thumbnail(
        (340, 340)
    )

    preview = ImageTk.PhotoImage(
        img
    )

    image_box.config(
        image=preview,
        text=""
    )


# -----------------------
# PREDICT
# -----------------------

def predict():

    result_label.config(
        text="Napoved še ni povezana z modelom"
    )


# -----------------------
# UI
# -----------------------

main = tk.Frame(
    root,
    bg="#F8F8FA"
)

main.pack(
    fill="both",
    expand=True,
    padx=45,
    pady=40
)


# LEFT PANEL

left = tk.Frame(
    main,
    bg="#F8F8FA"
)

left.pack(
    side="left",
    fill="y"
)


image_box = tk.Label(
    left,
    text="\n📷\n\nNaloži sliko\n\n(prepoznava bo dodana kasneje)",
    bg="white",
    width=32,
    height=18,
    bd=1,
    relief="flat",
    cursor="hand2",
    font=("Helvetica Neue", 13)
)

image_box.pack()

image_box.bind(
    "<Button-1>",
    lambda e: upload_image()
)


# RIGHT PANEL

right = tk.Frame(
    main,
    bg="#F8F8FA"
)

right.pack(
    side="right",
    fill="both",
    expand=True,
    padx=35
)


title = tk.Label(
    right,
    text="Podatki vozila",
    bg="#F8F8FA",
    font=(
        "Helvetica Neue",
        24,
        "bold"
    )
)

title.pack(
    anchor="w",
    pady=(0, 20)
)


def field(text):

    ttk.Label(
        right,
        text=text
    ).pack(
        anchor="w",
        pady=(10, 5)
    )


def combo(var, values):

    box = ttk.Combobox(
        right,
        textvariable=var,
        values=values,
        state="readonly"
    )

    box.pack(
        fill="x"
    )

    return box


field("Znamka")

znamka_dropdown = combo(
    znamka_var,
    list(cars.keys())
)

znamka_dropdown.bind(
    "<<ComboboxSelected>>",
    update_models
)


field("Model")

model_dropdown = combo(
    model_var,
    []
)

model_dropdown.bind(
    "<<ComboboxSelected>>",
    update_engines
)


field("Motor")

engine_dropdown = combo(
    engine_var,
    []
)

engine_dropdown.bind(
    "<<ComboboxSelected>>",
    update_hp
)


field("HP")

hp_dropdown = combo(
    hp_var,
    []
)


field("Število lastnikov")

combo(
    owners_var,
    [0, 1, 2, 3, 4, 5]
)


field("Št. kilometrov")

ttk.Entry(
    right,
    textvariable=km_var
).pack(
    fill="x"
)


field("Menjalnik")

combo(
    gearbox_var,
    [
        "Ročni",
        "Avtomatik"
    ]
)


field("Prva registracija")

combo(
    year_var,
    list(
        range(
            2026,
            2014,
            -1
        )
    )
)


ttk.Button(
    right,
    text="Napovej vrednost avtomobila",
    command=predict
).pack(
    fill="x",
    pady=40
)


result_label = tk.Label(
    right,
    text="",
    bg="#F8F8FA",
    font=(
        "Helvetica Neue",
        18,
        "bold"
    )
)

result_label.pack()


root.mainloop()