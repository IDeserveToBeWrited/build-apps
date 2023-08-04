from config import Config
import re
import requests


# Read release.json file
release = requests.get(Config.REVANCED_APKS_RELEASE_URL).json()


def revanced_version_message():
    return re.findall(r"CLI:[a-zA-Z-.\s0-9:]+\n", release["body"])[0].strip() or ""


def generate_file_bullet(file_name, file_url):
    return f"🔗 [{file_name}]({file_url})"


def generate_files_message():

    # Collect browser_download_url from assets in release
    nonroot_files = []
    root_files = []

    for asset in release["assets"][::-1]:
        file_name = asset["name"]
        file_url = asset["browser_download_url"]
        if ".zip" in file_name:
            root_files.append(generate_file_bullet(file_name, file_url))
        else:
            nonroot_files.append(generate_file_bullet(file_name, file_url))

    microg = fetch_microg()
    nonroot_files.append(
        generate_file_bullet(microg["microg_name"], microg["microg_file"])
    )

    return {"nonroot_files": nonroot_files, "root_files": root_files}


def fetch_microg():

    vanced_microg_release = requests.get(Config.MICROG_RELEASE_URL).json()

    microg_file = vanced_microg_release["assets"][0] or []

    microg_name = (
        microg_file["name"].strip(".apk")
        + "-"
        + vanced_microg_release["tag_name"]
        + ".apk"
        or "microg.apk"
    )
    microg_file = microg_file["browser_download_url"] or ""

    if "microg" in microg_file:
        return {"microg_name": microg_name, "microg_file": microg_file}
    else:
        # to avoid error returning empty string
        return {"microg_name": "", "microg_file": ""}


def main():
    files = generate_files_message()

    # Format release message
    release_message = Config.RELEASE_MESSAGE.format(
        release_name=release["name"],
        revanced_version_message=revanced_version_message(),
        notes=Config.NOTES,
        nonroot_files="\n".join(files["nonroot_files"]),
        root_files="\n".join(files["root_files"]),
        credits_message=Config.CREDITS_MESSAGE,
    )

    print(release_message)

    # Write release message to file
    with open("release_notification.md", "w") as f:
        f.write(release_message)
