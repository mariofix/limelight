from .version import __version_info_str__ as __version__


def get_context_data() -> dict:
    data = {
        "app_version": __version__,
    }
    return data
