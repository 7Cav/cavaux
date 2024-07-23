import os
import sys
import json
import argparse
import subprocess
import fileinput
import glob
import shutil

scriptPath   = os.path.realpath(__file__)
scriptRoot   = os.path.dirname(scriptPath)
PROJECTROOT  = os.path.dirname(os.path.dirname(scriptPath))

STEAMCMD     = os.path.join("steamcmd")
HEMTT        = os.path.join("hemtt")
ARMAKE       = os.path.join("armake")

WORKDIR      = os.path.join(PROJECTROOT,".cavauxout")
WORKSHOPOUT  = os.path.join(WORKDIR,"steamapps","workshop","content","107410")
HEMTTRELEASE = os.path.join(PROJECTROOT,".hemttout","release")


def obtain_and_update_version():
    result = subprocess.run(
        ["git", "describe", "--tags", "--abbrev=0"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    try:
        if result.returncode == 128:
            raise Exception("No git tags detected using 0.0.0 instead")
        tagVersion = result.stdout
    except Exception as e:
        print(e)
        tagVersion="0.0.0"

    tagVer = tagVersion.split('.')
    verMajor = tagVer[0]
    verMinor = tagVer[1]
    verPatch = tagVer[2]
    verBuild = 0

    hemttConf = os.path.join(PROJECTROOT,".hemtt","project.toml")
    try: 
        def replaceAll(file,searchExp,replaceExp):
            for line in fileinput.input(file, inplace=1):
                if searchExp in line:
                    line = line.replace(searchExp,replaceExp)
                sys.stdout.write(line)
        replaceAll(hemttConf, "major = 0", f"major = {verMajor}")
        replaceAll(hemttConf, "minor = 0", f"minor = {verMinor}")
        replaceAll(hemttConf, "patch = 0", f"patch = {verPatch}")
        replaceAll(hemttConf, "build = 0", f"build = {verBuild}")
    except FileNotFoundError as e:
        print(e);sys.exit(1)

    return tagVersion


def get_commit_id():
    result = subprocess.run(
        ['git','rev-parse','--short=8','HEAD~2'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    try:
        if result.returncode == 128:
            raise Exception("No git commitId detected using 'xxxxxxxx' instead")
        commitId = result.stdout
    except Exception as e:
        print(e)
        commitId="xxxxxxxx"

    commitId = commitId.replace('\n','')

    return commitId



def download_mod_files(complete_mod_list, STEAM_LOGIN, STEAM_PASS):
    login_cmd = [
        STEAMCMD,
        '+force_install_dir', WORKDIR,
        '+login', STEAM_LOGIN, STEAM_PASS,
    ]

    mods_cmd_parts = []
    for mod_id in complete_mod_list:
        mods_cmd_parts.extend(['+workshop_download_item', '107410', mod_id, 'validate'])

    full_cmd = login_cmd + mods_cmd_parts + ['+quit']

    print(f"Downloading mods...")
    try:
        subprocess.run(full_cmd, shell=True, check=False)
        print(f"Successfully downloaded mods")
    except subprocess.CalledProcessError as e:
        print(f"Failed to download mods: {e}")


def resign_mod(mod_folder):
    print(f"Resigning {mod_folder}")
    get_commit_id()
    print("TODO MAGIC MAGIC")
    print("TODO MAGIC MAGIC")
    print("TODO MAGIC MAGIC")
    print("TODO MAGIC MAGIC")
    print("TODO MAGIC MAGIC")
    print("TODO MAGIC MAGIC")


def main():
    parser = argparse.ArgumentParser(
        prog='ProgramName',
        description='What the program does',
        epilog='Text at the bottom of help')

    parser.add_argument('-u', '--username', type=str)
    parser.add_argument('-p', '--password', type=str)
    parser.add_argument('-C', '--config', type=str)
    parser.add_argument('-v', '--verbose', action='store_true')

    args = parser.parse_args()
    
    serverConfig = {
        "username": "",
        "password": ""
    }
    if args.config:
        try: 
            configFile = open(args.config)
        except FileNotFoundError as e:
            print(e);sys.exit(1)
        configFileDict = json.load(configFile)
        configFile.close()
        if "username" in configFileDict:
            serverConfig.update({"username": configFileDict["username"]})
        if "password" in configFileDict:
            serverConfig.update({"password": configFileDict["password"]})
    if args.username:
        serverConfig.update({"username": args.username})
    if args.password:
        serverConfig.update({"password": args.password})

    # Obtain list
    modListPath = os.path.join(PROJECTROOT, "cavAuxModList.json")
    try: 
        modListFile = open(modListPath)
    except FileNotFoundError:
        print(f"[ScriptError] {modListPath} does not exist in project root")
    modListDict = json.load(modListFile)
    modListFile.close()

    # Checking mod list
    print("Checking and verifying mod list")
    for category in modListDict.keys():
        if "workshop" in category:
            print(category)
            for id in modListDict[category]:
                print(f"> {modListDict[category][id]['name']} [{id}]")
                license = modListDict[category][id]['License']
                if license != "License permits":
                    print(f"  Non standard license agreement: '{license}'")
                requireResigning = modListDict[category][id]['requireResigning']
                if requireResigning:
                    print(f"  NOTE: {id} will be resigned.")
    print()


    # Create download and project working folder
    if not os.path.exists(WORKDIR):
        os.makedirs(WORKDIR)
    
    
    # Downloading mods from workshop
    print("Downloading mods from workshop")
    #subprocess.run(f"{steamcmdBinary} +quit", shell=True, check=args.verbose)
    #download_mod_files(modListDict['workshop'].keys(), serverConfig['username'], serverConfig["password"])

    # Check if mod have been downloaded properly and contain correct data
    allModsExist=True
    for downloadedMod in os.listdir(WORKSHOPOUT):
        if not downloadedMod in modListDict['workshop'].keys():
            print(f"[Error] {modListDict['workshop'][downloadedMod]['name']} [{downloadedMod}] does not exist or have not download properly")
            allModsExist=False

    if allModsExist:
        print("All mods successfully download")
        print()
    else: 
        sys.exit(1)

    # Assemble mod
    # Build mod
    version = obtain_and_update_version()
    subprocess.run(f"{HEMTT} release", shell=True, check=args.verbose)

    #for category in modListDict.keys():
    #    if "workshop" in category:
    #        for id in modListDict[category]:
    #            print(f"{modListDict[category][id]["name"]} [{id}]")
    #            modFolders = next(os.walk(os.path.join(WORKSHOPOUT,id)))[1]
    #            for folder in modFolders:
    #                if folder in ["addons","Addons"]:
    #                    content = len(glob.glob(os.path.join(WORKSHOPOUT,id,folder,'*')))
    #                    pbos = glob.glob(os.path.join(WORKSHOPOUT,id,folder,'*.pbo'))
    #                    bisign = glob.glob(os.path.join(WORKSHOPOUT,id,folder,'*.bisign'))
    #                    print(f"  PBO(s):    {len(pbos)}")
    #                    print(f"  bisign(s): {len(bisign)}")
    #                    print(f"  Total:     {content}")
    #                    if len(bisign) == 0 or modListDict[category][id]['requireResigning']:
    #                        print("WARNING: No mod not marked as requiring resigning tho no keys detected resigning it anyways")
    #                        resign_mod(os.path.join(WORKSHOPOUT,id))
    #            print()

    releaseFolder = os.path.join(WORKDIR,'release')
    releaseAddonFolder = os.path.join(releaseFolder,"addons")
    releaseKeysFolder = os.path.join(releaseFolder,"keys")
    if not os.path.exists(releaseFolder):
        os.makedirs(releaseFolder)
    if not os.path.exists(releaseAddonFolder):
        os.makedirs(releaseAddonFolder)
    if not os.path.exists(releaseKeysFolder):
        os.makedirs(releaseKeysFolder)

    commit = get_commit_id()

    print("Creating new key...")
    os.chdir(releaseKeysFolder)
    keyName = f"cavaux_{version}.0-{commit}"
    result = subprocess.run(
        [ARMAKE, 'keygen', '-f', keyName],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    print(result.stdout)
    os.chdir(PROJECTROOT)



    for id in os.listdir(WORKSHOPOUT):
        for pbo in glob.glob(os.path.join(WORKSHOPOUT,id,'**','*.pbo'), recursive=True):
            print(f"Copying {os.path.basename(pbo)}")
            shutil.copy2(os.path.join(pbo), releaseAddonFolder)

    # Copying over main mod
    shutil.copy2(os.path.join(HEMTTRELEASE,"mod.cpp"), releaseFolder)
    shutil.copy2(os.path.join(HEMTTRELEASE,"meta.cpp"), releaseFolder)
    shutil.copy2(os.path.join(HEMTTRELEASE,"logo_cav_ca.paa"), releaseFolder)
    for pbo in glob.glob(os.path.join(HEMTTRELEASE,'addons','*.pbo')):
        shutil.copy2(pbo, releaseAddonFolder)

    # Signing PBOS
    os.chdir(releaseAddonFolder)
    for pbo in glob.glob(os.path.join(releaseAddonFolder,'*.pbo')):
        print(f"Signing {pbo}")
        subprocess.run(
            [ARMAKE, 'sign', '-f', f"{os.path.join(releaseKeysFolder,f"{keyName}.biprivatekey")}", pbo],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )

    os.remove(os.path.join(releaseKeysFolder,f"{keyName}.biprivatekey"))




if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAborted")
        sys.exit(1)