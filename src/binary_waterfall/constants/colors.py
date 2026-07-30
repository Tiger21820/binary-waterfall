# ==============================================================================
# Material Design 3 (Material You) Color System
# ==============================================================================
# This implements a full M3 tonal palette based on a seed color.
# The system uses two key concepts:
#   - TonalPalette: 13 tones (0-100) for a single hue family
#   - Scheme: maps semantic roles (primary, surface, etc.) to specific tones
#
# Light scheme: dark text on light surfaces
# Dark scheme: light text on dark surfaces
#
# Key roles and their dark-theme tone mapping:
#   primary          = 80  (vibrant, for key components)
#   on-primary       = 20  (content on primary)
#   primary-container= 30  (filled variant)
#   secondary        = 80  (less prominent)
#   surface          = 6   (darkest background)
#   surface-variant  = 12  (elevated surfaces)
#   surface-container = 10 (card backgrounds)
#   surface-bright   = 24  (brightest surface)
#   on-surface       = 90  (primary text)
#   on-surface-variant= 80 (secondary text)
#   outline          = 60  (borders, dividers)
#   outline-variant  = 30  (subtle borders)
#   error            = 80  (error state)
#   scrim            = 0   (backdrop)
# ==============================================================================

# MD3 reference tones for dark theme
_TONE_PRIMARY = 80
_TONE_ON_PRIMARY = 20
_TONE_PRIMARY_CONTAINER = 30
_TONE_ON_PRIMARY_CONTAINER = 90
_TONE_SECONDARY = 80
_TONE_ON_SECONDARY = 20
_TONE_SECONDARY_CONTAINER = 30
_TONE_ON_SECONDARY_CONTAINER = 90
_TONE_TERTIARY = 80
_TONE_ON_TERTIARY = 20
_TONE_TERTIARY_CONTAINER = 30
_TONE_ON_TERTIARY_CONTAINER = 90
_TONE_ERROR = 80
_TONE_ON_ERROR = 20
_TONE_ERROR_CONTAINER = 30
_TONE_ON_ERROR_CONTAINER = 90
_TONE_SURFACE = 6
_TONE_SURFACE_VARIANT = 12
_TONE_SURFACE_CONTAINER = 10
_TONE_SURFACE_CONTAINER_HIGH = 17
_TONE_SURFACE_CONTAINER_HIGHEST = 22
_TONE_SURFACE_BRIGHT = 24
_TONE_ON_SURFACE = 90
_TONE_ON_SURFACE_VARIANT = 80
_TONE_OUTLINE = 60
_TONE_OUTLINE_VARIANT = 30
_TONE_INVERSE_SURFACE = 90
_TONE_INVERSE_ON_SURFACE = 20
_TONE_INVERSE_PRIMARY = 40
_TONE_SCRIM = 0

# Helper: convert tone value (0-100) to hex luminance string
#   tone 0  = #000000 (black)
#   tone 100 = #ffffff (white)
# We use simplified interpolation for a clean M3 look.
def _tone_to_hex(tone):
    """Convert a tone 0-100 to a hex color approximating M3 luminance."""
    v = round(tone * 2.55)
    return f"#{v:02x}{v:02x}{v:02x}"


# ----- Dark Theme Colors (default) -----
# Based on a green/teal seed color for the primary palette.
_PRIMARY_DARK = "#3ddbac"
_PRIMARY_LIGHT = "#006c4c"

_SECONDARY_DARK = "#b8ccbd"
_SECONDARY_LIGHT = "#4e6355"

_TERTIARY_DARK = "#a0cfdf"
_TERTIARY_LIGHT = "#3d6472"

_ERROR_DARK = "#ffb4ab"
_ERROR_LIGHT = "#ba1a1a"

COLORS_DARK = {
    # Primary
    "primary":               _PRIMARY_DARK,
    "on_primary":            _tone_to_hex(_TONE_ON_PRIMARY),
    "primary_container":     _tone_to_hex(_TONE_PRIMARY_CONTAINER),
    "on_primary_container":  _tone_to_hex(_TONE_ON_PRIMARY_CONTAINER),

    # Secondary
    "secondary":               _SECONDARY_DARK,
    "on_secondary":            _tone_to_hex(_TONE_ON_SECONDARY),
    "secondary_container":     _tone_to_hex(_TONE_SECONDARY_CONTAINER),
    "on_secondary_container":  _tone_to_hex(_TONE_ON_SECONDARY_CONTAINER),

    # Tertiary
    "tertiary":               _TERTIARY_DARK,
    "on_tertiary":            _tone_to_hex(_TONE_ON_TERTIARY),
    "tertiary_container":     _tone_to_hex(_TONE_TERTIARY_CONTAINER),
    "on_tertiary_container":  _tone_to_hex(_TONE_ON_TERTIARY_CONTAINER),

    # Error
    "error":               _ERROR_DARK,
    "on_error":            _tone_to_hex(_TONE_ON_ERROR),
    "error_container":     _tone_to_hex(_TONE_ERROR_CONTAINER),
    "on_error_container":  _tone_to_hex(_TONE_ON_ERROR_CONTAINER),

    # Surface / Background
    "background":       _tone_to_hex(_TONE_SURFACE),
    "surface":          _tone_to_hex(_TONE_SURFACE),
    "surface_variant":  _tone_to_hex(_TONE_SURFACE_VARIANT),
    "surface_container": _tone_to_hex(_TONE_SURFACE_CONTAINER),
    "surface_container_high": _tone_to_hex(_TONE_SURFACE_CONTAINER_HIGH),
    "surface_container_highest": _tone_to_hex(_TONE_SURFACE_CONTAINER_HIGHEST),
    "surface_bright":   _tone_to_hex(_TONE_SURFACE_BRIGHT),

    # On Surface
    "on_surface":         _tone_to_hex(_TONE_ON_SURFACE),
    "on_surface_variant": _tone_to_hex(_TONE_ON_SURFACE_VARIANT),

    # Outline
    "outline":         _tone_to_hex(_TONE_OUTLINE),
    "outline_variant": _tone_to_hex(_TONE_OUTLINE_VARIANT),

    # Inverse
    "inverse_surface":    _tone_to_hex(_TONE_INVERSE_SURFACE),
    "inverse_on_surface": _tone_to_hex(_TONE_INVERSE_ON_SURFACE),
    "inverse_primary":    _tone_to_hex(_TONE_INVERSE_PRIMARY),

    # Scrim
    "scrim": _tone_to_hex(_TONE_SCRIM),

    # Viewer (the image display area)
    "viewer": "#000000",
}

# Light Theme Colors
COLORS_LIGHT = {
    "primary":               _PRIMARY_LIGHT,
    "on_primary":            "#ffffff",
    "primary_container":     "#9af2cf",
    "on_primary_container":  "#002114",

    "secondary":               _SECONDARY_LIGHT,
    "on_secondary":            "#ffffff",
    "secondary_container":     "#b8ccbd",
    "on_secondary_container":  "#0c1f14",

    "tertiary":               _TERTIARY_LIGHT,
    "on_tertiary":            "#ffffff",
    "tertiary_container":     "#b6eafb",
    "on_tertiary_container":  "#001f29",

    "error":               _ERROR_LIGHT,
    "on_error":            "#ffffff",
    "error_container":     "#ffdad6",
    "on_error_container":  "#410002",

    "background":             "#fbfcf8",
    "surface":                "#fbfcf8",
    "surface_variant":        "#dce5dc",
    "surface_container":      "#eff1ec",
    "surface_container_high": "#e9ebe6",
    "surface_container_highest": "#e3e5e0",
    "surface_bright":         "#fbfcf8",

    "on_surface":         "#191d1a",
    "on_surface_variant": "#424940",

    "outline":         "#72796f",
    "outline_variant": "#c2c9be",

    "inverse_surface":    "#2d322e",
    "inverse_on_surface": "#f0f2ed",
    "inverse_primary":    "#6ddbaf",

    "scrim": "#000000",
    "viewer": "#ffffff",
}

# Default to dark theme
COLORS = COLORS_DARK

# MD3 Shape / Radius constants
SHAPES = {
    "none": 0,
    "extra_small": 4,
    "small": 8,
    "medium": 12,
    "large": 16,
    "extra_large": 28,
    "full": 9999,
}

# MD3 Typography sizes (in px)
TYPESET = {
    "display_large": 57,
    "display_medium": 45,
    "display_small": 36,
    "headline_large": 32,
    "headline_medium": 28,
    "headline_small": 24,
    "title_large": 22,
    "title_medium": 16,
    "title_small": 14,
    "body_large": 16,
    "body_medium": 14,
    "body_small": 12,
    "label_large": 14,
    "label_medium": 12,
    "label_small": 11,
}

# MD3 Elevation (shadow) levels in px
ELEVATION = {
    "level_0": 0,
    "level_1": 1,
    "level_2": 3,
    "level_3": 6,
    "level_4": 8,
    "level_5": 12,
}