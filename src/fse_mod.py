import os
import json
import glob
import yaml
import _logging
import re

logger = _logging.getLogger(__name__)

with open("subtable.json", "r") as fp:
    rpy_sub_table = json.load(fp)


class Package(object):

    def __init__(self, package_dir):
        super().__init__()
        self.root = package_dir

        self._scriptfiles = []
        self._archivefiles = []

        self.loadMetadata()
        self.loadCredits()

    @property
    def achievements(self):
        return self.metadata["achievements"]

    @property
    def id(self):
        return self.metadata["package_id"]

    @property
    def public(self):
        return self.metadata.get("public", False)

    @property
    def private(self):
        return not self.public

    @property
    def volumes(self):
        return self.metadata["volumes"]

    @property
    def assets_dir(self):
        return os.path.join(self.root, "assets")
    
    @property
    def assets_common_dir(self):
        return os.path.join(self.root, "assets_common")

    def loadMetadata(self):
        self.meta_filepath = os.path.join(self.root, "meta.json")
        with open(self.meta_filepath, "r", encoding="utf-8") as fp:
            self.metadata = json.load(fp)
        self.correctMetadata()

    def correctMetadata(self):
        for volume in self.metadata["volumes"]:
            volume["package_id"] = self.id

        self.metadata["achievements"] = self.metadata.get("achievements", [])
        for achievement in self.metadata["achievements"]:
            achievement["package_id"] = self.id
            achievement["_id"] = f"{self.id}_{achievement['id_suffix']}"
            achievement["_img_locked"] = self.subtableReplace("{{assets}}/" + achievement["img_locked"])
            achievement["_img_unlocked"] = self.subtableReplace("{{assets}}/" + achievement["img_unlocked"])

    def loadCredits(self):
        credits_filepath = os.path.join(self.root, "credits.yml")
        if os.path.isfile(credits_filepath):
            with open(credits_filepath, "r", encoding="utf-8") as fp:
                self.credits = yaml.safe_load(self.subtableReplace(fp.read()))
        else:
            self.credits = None

    def getScriptFiles(self):
        if not self._scriptfiles:
            self._scriptfiles = glob.glob(os.path.join(self.root, "*.rpy"))
        for rpy in self._scriptfiles:
            yield rpy

    def getArchiveFiles(self):
        if not self._archivefiles:
            self._archivefiles = glob.glob(os.path.join(self.root, "*.rpa"))
        for rpa in self._archivefiles:
            yield rpa

    def subtableReplace(self, textdata, subtable=rpy_sub_table):
        return subtableReplace(textdata, self.metadata, subtable=subtable)


class DummyPackage(Package):

    def loadMetadata(self):
        self.metadata = {
            "package_id": "pid",
            "volumes": [
                {
                    "volume_id": "vid",
                    "title": "title",
                    "subtitle": "pull quote",
                    "author": "author"
                }
            ]
        }
        self.correctMetadata()

    def loadCredits(self):
        self.credits = None


dummy_package = DummyPackage(None)


def subtableReplace(textdata, fstrings=dummy_package.metadata, subtable=rpy_sub_table):
    for rtype, pattern, repl in subtable:
        if rtype == "R":
            textdata = re.sub(pattern, repl, textdata, flags=re.MULTILINE)
        elif rtype == "S":
            try:
                if pattern in textdata:
                    textdata = textdata.replace(pattern, repl.format(**fstrings))
            except KeyError:
                logger.error("Availible keys:", fstrings.keys(), exc_info=True)
                raise
    return textdata


def getAllPackages(fse_base, only_volumes=False):
    all_packages = []
    warn = False

    filtering_volumes = (only_volumes != [])
    only_volumes.append("sys")

    # Detect misplaced mods
    meta_files = glob.glob(os.path.join(fse_base, "custom_volumes", "**", "meta.json"), recursive=True)
    for meta_file in meta_files:
        mod_dir = os.path.dirname(meta_file)
        containing_dir = os.path.dirname(mod_dir)
        if os.path.split(containing_dir)[1].lower() != "custom_volumes":
            logger.warn(f"Mod folder '{os.path.split(mod_dir)[1].lower()}' is in {containing_dir}, not 'custom_volumes'.")
            logger.warn(f"In order to run this mod, move {mod_dir} directly to 'custom_volumes'.\n")
            warn = True

    for archive in (
        glob.glob(os.path.join(fse_base, "custom_volumes", "*.zip")) +
        glob.glob(os.path.join(fse_base, "custom_volumes", "*.rar")) +
        glob.glob(os.path.join(fse_base, "custom_volumes", "*.7z"))
    ):
        archive_name = os.path.split(archive)[1]
        archive_name_plain = os.path.splitext(archive_name)[0]
        logger.warn(f"Found unextracted archive '{archive_name}'.")
        logger.warn(f"Extract archives such that 'meta.json' is in a mod folder that is in 'custom_volumes', i.e. 'custom_volumes/{archive_name_plain}/meta.json'.")
        warn = True

    SYSDIR = os.path.join(fse_base, "src", "sys/")
    for subdir in [SYSDIR] + glob.glob(os.path.join(fse_base, "custom_volumes", "*/")):
        try:
            package = Package(subdir)
            logger.info(f"Detected package {package.id} at {package.root}")

            if filtering_volumes and package.id not in only_volumes:
                continue

            all_packages.append(package)

        except FileNotFoundError as e:
            logger.error(f"Missing configuration file {e}, required!")
            warn = True
            continue
        except json.decoder.JSONDecodeError:
            logger.error("Invalid json file at '%s'", os.path.join(subdir, "meta.json"))
            logger.error("Ensure that this file is valid JSON; try an online json linter/validator if issues persist.")
            warn = True
            continue

    if filtering_volumes:
        for package_id in only_volumes:
            if not any(p.id == package_id for p in all_packages):
                logger.warn(f"[WARNING]\tIncluded package {package_id} not found!")
                warn = True

    return all_packages, warn


if __name__ == "__main__":
    # test
    betas = Package("../custom_volumes_other/pq_betas/")
    openb = Package("../custom_volumes_other/openbound/")
