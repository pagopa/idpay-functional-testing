import tempfile

import gnupg


def pgp_file_routine(file_path: str, pgp_key_data: str):
    with tempfile.TemporaryDirectory() as temp_gpg_home:
        gpg = gnupg.GPG(gnupghome=temp_gpg_home)
        import_result = gpg.import_keys(pgp_key_data)
        output_path = f"{file_path}.pgp"
        with open(file_path, "rb") as f:
            status = gpg.encrypt_file(
                f,
                recipients=import_result.results[0]["fingerprint"],
                output=output_path,
                extra_args=["--openpgp", "--trust-model", "always"],
                armor=False,
            )
            if status.ok:
                return output_path
    return None


def pgp_string_routine(data_to_encrypt: str, pgp_key_data: str):
    with tempfile.TemporaryDirectory() as temp_gpg_home:
        gpg = gnupg.GPG(gnupghome=temp_gpg_home)
        import_result = gpg.import_keys(pgp_key_data)
        status = gpg.encrypt(
            data_to_encrypt,
            recipients=import_result.results[0]["fingerprint"],
            extra_args=["--trust-model", "always"],
        )
        if status.ok:
            return status.data
    return None
