import tempfile
from pathlib import Path

import git

from modules.config import config
from modules.crypto import encrypt
from modules.logger import get_logger
from modules.models import ExportObjectList


def export_git(data: ExportObjectList) -> None:
    logger = get_logger()

    if config.outputs.git.enable:
        if config.general.dryrun:
            logger.info("Dryrun enabled, skipping git export")
        else:
            logger.info("Exporting to git")
            with tempfile.TemporaryDirectory() as tmpdirname:
                repo = git.Repo.clone_from(
                    config.outputs.git.repo,
                    tmpdirname,
                    depth=1,
                    sparse=True,
                )
                repo.git.rm("-r", "--sparse", ".")

                for exportdata in data:
                    export_dir = Path(tmpdirname) / Path(exportdata.type)
                    export_filename = Path(export_dir) / Path(
                        f"{exportdata.name_sanitized}_{exportdata.id}.{config.zabbix.export_format}",
                    )

                    Path.mkdir(export_dir, exist_ok=True)
                    if config.general.encryption or config.inputs.model_dump()[exportdata.type]["encryption"]:
                        with Path.open(export_filename, "wb") as export_file:
                            export_file.write(encrypt(exportdata.data, config.general.encryption_key))
                    else:
                        with Path.open(export_filename, "w") as export_file:
                            export_file.write(exportdata.data)

                repo.git.add(".", "--sparse")
                repo_changes = repo.git.status("--porcelain")
                if repo_changes:
                    logger.debug("Changes to commit:")
                    for change in repo_changes.split("\n"):
                        logger.debug(f"    {change}")
                    repo.git.commit("-m", "Exported data")
                    repo.git.push()
    else:
        logger.debug("Git export disabled")
