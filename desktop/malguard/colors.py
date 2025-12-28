"""
Color utilities for terminal output.
Uses colorama for cross-platform colored text.
"""

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False
    # Fallback - no colors
    class Fore:
        RED = GREEN = YELLOW = CYAN = MAGENTA = WHITE = RESET = ""
    class Style:
        BRIGHT = DIM = RESET_ALL = ""


class Colors:
    """Color codes for terminal output."""
    
    # Status colors
    SUCCESS = Fore.GREEN
    DANGER = Fore.RED
    WARNING = Fore.YELLOW
    INFO = Fore.CYAN
    MUTED = Style.DIM
    
    # Severity colors
    CRITICAL = Fore.RED + Style.BRIGHT
    HIGH = Fore.RED
    MEDIUM = Fore.YELLOW
    LOW = Fore.GREEN
    
    # Reset
    RESET = Style.RESET_ALL
    
    @classmethod
    def severity(cls, level: str) -> str:
        """Get color for severity level."""
        colors = {
            'critical': cls.CRITICAL,
            'high': cls.HIGH,
            'medium': cls.MEDIUM,
            'low': cls.LOW
        }
        return colors.get(level.lower(), "")
    
    @classmethod
    def success(cls, text: str) -> str:
        return f"{cls.SUCCESS}{text}{cls.RESET}"
    
    @classmethod
    def danger(cls, text: str) -> str:
        return f"{cls.DANGER}{text}{cls.RESET}"
    
    @classmethod
    def warning(cls, text: str) -> str:
        return f"{cls.WARNING}{text}{cls.RESET}"
    
    @classmethod
    def info(cls, text: str) -> str:
        return f"{cls.INFO}{text}{cls.RESET}"
    
    @classmethod
    def muted(cls, text: str) -> str:
        return f"{cls.MUTED}{text}{cls.RESET}"


# Shorthand functions
def green(text: str) -> str:
    return Colors.success(text)

def red(text: str) -> str:
    return Colors.danger(text)

def yellow(text: str) -> str:
    return Colors.warning(text)

def cyan(text: str) -> str:
    return Colors.info(text)

def dim(text: str) -> str:
    return Colors.muted(text)
