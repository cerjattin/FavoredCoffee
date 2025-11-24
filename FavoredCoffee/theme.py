import reflex as rx

# --- 1. Constantes de Color (VITALES para que no fallen las páginas) ---
# Estas son usadas directamente en tus botones y gradientes.
COLOR_PURPLE = "#6A3587"
COLOR_MAGENTA = "#D94A8A"
COLOR_CORAL = "#EB7A74"

# --- 2. Configuración del Tema ---
app_theme = rx.theme(
    appearance="light",
    has_background=True,
    radius="large",
    # Usamos 'plum' como acento principal (es lo más parecido a tu morado/magenta en el estándar)
    accent_color="plum", 
)

# Sobrescribimos la función rx.color original para interceptar tus colores
_original_color = rx.color

def safe_color(color_name, shade=7, alpha=False):
    # Mapeamos tus nombres a los estándares más cercanos
    map_colors = {
        "magenta": "plum",  # Tu magenta se verá como Plum (Ciruela)
        "coral": "tomato",  # Tu coral se verá como Tomato
        "purple": "iris",   # Tu purple se verá como Iris
    }
    
    # Si el color es uno de los tuyos, usamos el estándar
    final_name = map_colors.get(color_name, color_name)
    return _original_color(final_name, shade, alpha)

# Inyectamos nuestra función segura
rx.color = safe_color