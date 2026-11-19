"""Entry point: python -m receiver"""

import logging
from src.utils.logger import setup_logging
from .app import ReceiverApp


def main() -> None:
    setup_logging()
    app = ReceiverApp()
    app.mainloop()


if __name__ == "__main__":
    main()
