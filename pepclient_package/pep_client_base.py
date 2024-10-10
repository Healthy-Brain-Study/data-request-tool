import json
import subprocess
import tempfile
import threading


class PepClientBase:
    """
    A class used to interact with the PEP client (Polymorphic encryption and pseudonymisation for personalised healthcare) using command-line operations.
    It supports operations such as listing, storing, and modifying data entries based on authentication methods.
    """

    def __init__(self, pep_token_filepath="", production=True, auth_method="token"):
        """
        Initialize the PEP client base.

        Args:
            pep_token_filepath (str): The file path to the authentication token.
            production (bool): Flag to indicate if the production environment should be used.
            auth_method (str): The authentication method to use ("token" or "logon").

        Raises:
            ValueError: If the authentication method is neither 'token' nor 'logon'.
        """
        self.pep_token_filepath = pep_token_filepath
        self.production = production
        self.timeout = None

        if auth_method not in ["logon", "token"]:
            raise ValueError(f"Parameter 'auth_method' must be either 'token' or 'logon'. Current value '{auth_method}' is neither.")

        self.auth_method = auth_method
        self.base_command = self._build_base_command()
        self.lock = threading.Lock()

        if self.auth_method == "logon":
            self.temp_dir_logon = tempfile.TemporaryDirectory()

    def set_timeout(self, timeout):
        """
        Set the timeout for the command execution.

        Args:
            timeout (int): The timeout value in seconds.
        """
        self.timeout = timeout

    def reset_timeout(self):
        """
        Reset the timeout to None.
        """
        self.timeout = None

    def _check_pepcli_path(self):
        """
        Check the PEP CLI path. Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclass must implement abstract method")

    def _build_base_command(self):
        """
        Build the base command for interaction. Must be overridden in subclasses.
        """
        raise NotImplementedError("Subclass must implement abstract method")

    def _command(self, command):
        """
        Execute a command using the appropriate authentication method.

        Args:
            command (str): The command to execute.

        Returns:
            tuple: The output of the command and the exit code.
        """
        full_command = f"{self.base_command} {command}"
        result = []

        if self.auth_method == "logon":
            result, exit_code = self._command_auth_method_logon(full_command)
        else:
            result, exit_code = self._command_auth_method_token(full_command)

        return self.pep_command_parser(result, exit_code)

    def _command_auth_method_token(self, full_command):
        """
        Execute a command using token-based authentication.

        Args:
            full_command (str): The full command to execute.

        Returns:
            tuple: The output and exit code of the command execution.
        """
        try:
            with tempfile.TemporaryDirectory() as tempdir:
                process = subprocess.run(full_command, capture_output=True, encoding="ISO-8859-1", shell=True, cwd=tempdir, timeout=self.timeout)
                exit_code = process.returncode

                if exit_code != 0:
                    result = process.stderr
                else:
                    result = process.stdout
        except subprocess.CalledProcessError as e:
            exit_code = e.returncode
            result = e.output

        return (result, exit_code)

    def _command_auth_method_logon(self, full_command):
        """
        Execute a command using logon-based authentication.

        Args:
            full_command (str): The full command to execute.

        Returns:
            tuple: The output and exit code of the command execution.
        """
        try:
            with self.lock:
                process = subprocess.run(full_command, capture_output=True, encoding="ISO-8859-1", shell=True, cwd=self.temp_dir_logon.name, timeout=self.timeout)
            exit_code = process.returncode

            if exit_code != 0:
                result = process.stderr
            else:
                result = process.stdout
        except subprocess.CalledProcessError as e:
            exit_code = e.returncode
            result = e.output

        return (result, exit_code)

    def list(self, column_names, participant_ids, no_inline_data=True):
        """
        List data entries for specified columns and participants.

        Args:
            column_names (list or str): The column names to list.
            participant_ids (list or str): The participant IDs to list.
            no_inline_data (bool): Flag to not include inline data.

        Returns:
            tuple: The output of the command and the exit code.

        Raises:
            ValueError: If no columns or participants are specified.
        """
        if isinstance(column_names, str):
            column_names = [column_names]
        if isinstance(participant_ids, str):
            participant_ids = [participant_ids]

        if not column_names:
            raise ValueError("At least one column must be specified.")
        if not participant_ids:
            raise ValueError("At least one participant must be specified.")

        columns_part = ' '.join([f'-c {column}' for column in column_names])
        participants_part = ' '.join([f'-p {participant}' for participant in participant_ids])
        command = f"list {columns_part} {participants_part}"

        if no_inline_data:
            command += " --no-inline-data"

        return self._command(command)

    def store(self, column_name, participant_id, filepath_or_data, file=True):
        """
        Store data for a specific column and participant.

        Args:
            column_name (str): The column name where data will be stored.
            participant_id (str): The participant ID for whom data will be stored.
            filepath_or_data (str): The file path or data to store.
            file (bool): Flag to specify if the input is a file (True) or data (False).

        Returns:
            tuple: The output of the command and the exit code.
        """
        if file:
            command = f"store -c {column_name} -p {participant_id} -i {filepath_or_data}"
        else:
            command = f"store -c {column_name} -p {participant_id} -d {filepath_or_data}"

        return self._command(command)

    def column_group_create(self, column_group_name, suffix=".columnGroup"):
        """
        Create a new column group.

        Args:
            column_group_name (str): The name of the column group to create.
            suffix (str): Suffix to append to the column group name.

        Returns:
            tuple: The output of the command and the exit code.
        """
        return self._command(f"ama columnGroup create {column_group_name}{suffix}")

    def column_group_add(self, column_group_name, column_name, suffix=".columnGroup"):
        """
        Add a column to an existing column group.

        Args:
            column_group_name (str): The name of the column group.
            column_name (str): The column name to add to the group.
            suffix (str): Suffix to append to the column group name during the operation.

        Returns:
            tuple: The output of the command and the exit code.
        """
        return self._command(f"ama column addTo {column_name} {column_group_name}{suffix}")

    def participant_group_create(self, participant_group_name, prefix="Participants."):
        """
        Create a new participant group.

        Args:
            participant_group_name (str): The name of the participant group to create.
            prefix (str): Prefix to prepend to the participant group name.

        Returns:
            tuple: The output of the command and the exit code.
        """
        return self._command(f"ama group create {prefix}{participant_group_name}")

    def participant_group_add(self, participant_group_name, participant_id, prefix="Participants."):
        """
        Add a participant to an existing participant group.

        Args:
            participant_group_name (str): The name of the participant group.
            participant_id (str): The participant ID to add to the group.
            prefix (str): Prefix to prepend to the participant group name during the operation.

        Returns:
            tuple: The output of the command and the exit code.
        """
        return self._command(f"ama group addTo {prefix}{participant_group_name} {participant_id}")

    def query_enrollment(self):
        """
        Query the enrollment status.

        Returns:
            tuple: The output of the command and the exit code.
        """
        return self._command("query enrollment")

    def query_column_access(self):
        """
        Query the access level for columns.

        Returns:
            tuple: The output of the command and the exit code.
        """
        return self._command("query column-access")

    def pull(self,
             target_folder='',
             force=False, resume=False,
             update=False,
             assume_pristine=False,
             update_pseudonym_format=False,
             all_accessible=False,
             columns=None,
             column_groups=None,
             participant_groups=None,
             participants=None,
             short_pseudonyms=None,
             report_progress=True):
        """
        Pull data from the server with various options.

        Args:
            target_folder (str): The target directory for downloaded files.
            force (bool): Force the download even if it might overwrite existing files.
            resume (bool): Resume an interrupted download.
            update (bool): Update existing files.
            assume_pristine (bool): Assume that files on the server are pristine.
            update_pseudonym_format (bool): Update the pseudonym format in downloaded files.
            all_accessible (bool): Download all accessible data.
            columns (list): Specific columns to download.
            column_groups (list): Specific column groups to download.
            participant_groups (list): Specific participant groups to download.
            participants (list): Specific participants to download.
            short_pseudonyms (list): Use short pseudonyms for participant identification.
            report_progress (bool): Flag to report progress during the download.
        Returns:
        tuple: The output of the command and the exit code.

        Raises:
            ValueError: If non-list parameters for list-type parameters are provided, or if the 'target_folder' is not a string.
        """
        command_parts = ['pull']
        flag_map = {
            'force': ('--force', force),
            'resume': ('--resume', resume),
            'update': ('--update', update),
            'assume_pristine': ('--assume-pristine', assume_pristine),
            'update_pseudonym_format': ('--update-pseudonym-format', update_pseudonym_format),
            'all_accessible': ('--all-accessible', all_accessible),
            'report_progress': ('--report-progress', report_progress)
        }

        for param, (flag, value) in flag_map.items():
            if value:
                command_parts.append(flag)

        list_param_map = {
            'columns': ('--columns', columns),
            'column_groups': ('--column-groups', column_groups),
            'participant_groups': ('--participant-groups', participant_groups),
            'participants': ('--participants', participants),
            'short_pseudonyms': ('--short-pseudonyms', short_pseudonyms)
        }

        for param, (flag, values) in list_param_map.items():
            if values:
                if not isinstance(values, list):
                    raise ValueError(f"Expected a list for '{param}' but got {type(values).__name__}")
                for value in values:
                    command_parts.append(f'{flag} {value}')

        if target_folder:
            if not isinstance(target_folder, str):
                raise ValueError(f"Expected a string for 'target_folder' but got {type(target_folder).__name__}")
            command_parts.append(f'--output-directory "{target_folder}"')

        command = ' '.join(command_parts)
        return self._command(command)

    def pep_command_parser(self, output, exit_code):
        """
        Parse the command output and determine the success based on the exit code.

        Args:
            output (str): The raw output from the command execution.
            exit_code (int): The exit code of the command execution.

        Returns:
            dict: A dictionary containing parsed data or error information based on command execution results.
        """
        succeeded = True if exit_code == 0 else False

        if output:
            try:
                json_data = json.loads(output)  # Load JSON string into Python object

                if json_data == []:
                    return {"data_found": False, "message": "Empty list found", "data": json_data, "error": not succeeded, "json_error": False}
                else:
                    return {"data_found": True, "message": "Data found", "data": json_data, "error": not succeeded, "json_error": False}
            except json.JSONDecodeError as e:
                return {"data_found": True, "message": output.strip(), "data": None, "error": not succeeded, "json_error": True, "json_message": (f"Error decoding JSON: {e}")}
        else:
            return {"data_found": False, "message": output.strip(), "data": None, "error": not succeeded, "json_error": False}
