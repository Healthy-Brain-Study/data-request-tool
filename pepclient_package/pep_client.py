# Factory function to return the appropriate PepClient based on the OS
import platform

from .pep_client_singularity import PepClientSingularity
from .pep_client_windows import PepClientWindows
from .pep_client_docker import PepClientDocker


def PepClient(pep_token_filepath="", production=True, auth_method="token", engine=None):
    """
    Factory function to create and return an instance of a PEP client based on the specified OS or the engine provided.

    The function dynamically selects the appropriate client type (Docker, Singularity, or Windows)
    depending on the platform the script is executed on or based on an explicitly specified engine.

    Args:
        pep_token_filepath (str): The file path to the PEP authentication token.
        production (bool): Flag to determine whether the client should run in production mode.
        auth_method (str): Method of authentication, default is by token.
        engine (str, optional): Explicit specification of the engine to use ('docker', 'singularity', 'windows').

    Returns:
        An instance of one of the PEP client types depending on the operating system or the specified engine.

    Raises:
        ValueError: If the operating system is not supported and no engine is specified.
    """
    os_name = platform.system().lower()

    if engine == "docker":
        return PepClientDocker(pep_token_filepath=pep_token_filepath, production=production, auth_method=auth_method)
    elif engine == "singularity":
        return PepClientSingularity(pep_token_filepath=pep_token_filepath, production=production, auth_method=auth_method)
    elif engine == "windows":
        return PepClientWindows(pep_token_filepath=pep_token_filepath, production=production, auth_method=auth_method)
    elif engine is not None and engine != "":
        raise ValueError(f"Unsupported engine: {engine}. Please specify engine or switch OS.")

    if os_name == 'linux':
        return PepClientSingularity(pep_token_filepath=pep_token_filepath, production=production, auth_method=auth_method)
    elif os_name == 'windows':
        return PepClientWindows(pep_token_filepath=pep_token_filepath, production=production, auth_method=auth_method)
    elif os_name == 'darwin':
        return PepClientDocker(pep_token_filepath=pep_token_filepath, production=production, auth_method=auth_method)
    else:
        raise ValueError(f"Unsupported operating system: {os_name}. Please specify engine or switch OS.")
