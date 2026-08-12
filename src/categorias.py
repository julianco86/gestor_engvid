CATEGORIAS = [
    "business english",
    "comprehension",
    "culture & tips",
    "english resource",
    "expressions",
    "grammar",
    "ielts",
    "pronunciation",
    "slang",
    "speaking",
    "vocabulary",
    "writing",
]

NIVELES = ["Beginner", "Intermediate", "Advanced"]

NIVEL_ORDEN = {"Beginner": 1, "Intermediate": 2, "Advanced": 3}


def detectar_categorias(texto):
    """Devuelve una lista de categorías conocidas presentes en el texto."""
    if not isinstance(texto, str) or not texto.strip():
        return []
    t = texto.lower()
    return [c for c in CATEGORIAS if c in t]


def categorias_como_texto(texto):
    """Devuelve las categorías detectadas unidas por comas ('' si no hay)."""
    return ", ".join(detectar_categorias(texto))
