from zipfile import ZipFile as zipFile
import os, random, json, time, shutil

''' Replacement search values:
        For a string do 'version' or "version".
        For a int give only a number like 90.
        For a json list give the input like like this; [item1, item2, item3].
        For a json object put in {"key":"value", "key2":"value"}

    To use the values input it into the following 2 variables.
    Be aware that this program doesn't check the input so please make a backup before its run in a folder
'''
replaceSearchKey = None     # like: "Version"
replaceValueWith = None     # Like: {"OS": 404, "game": 101}
                            #   Or: 420


def searchDirFor(directory, startsW, endsW):
    ''' Searches recursively in the specified directory for files that start with "startW" and end with "endsW" '''
    foundTarget = []

    for file in os.listdir(directory):
        if (file.endswith(endsW) and file.startswith(startsW)):
            foundTarget.append(os.path.join(directory, file));

        elif (os.path.isdir(os.path.join(directory, file))):
            foundTarget += searchDirFor(os.path.join(directory, file), startsW, endsW)
    return foundTarget


def displayArray(array, description):
    ''' Does as the name says with a nice & readable format '''
    temp = ''
    for i in range(len(array)):
        if len(temp) == 0:
            temp += '"'+array[i]+'"'
        elif i+1 == len(array):
            temp += ' and "'+array[i]+'"'
        else:
            temp += ', "'+array[i]+'"'
    print(timeStamp(timeStart),description+':', temp)


def getFileName(directory):
    ''' Gets the name of the specified file without extension and dictionary '''
    splitUpDirectory = allZips[i].split('/')
    fileName = splitUpDirectory[len(splitUpDirectory)-1].rsplit('.', 1)[0]
    return fileName


def jsonChangeValue(file, key, value):
    ''' Reads specified json file, changes it and saves that change '''
    print(f'{timeStamp(timeStart)} Changing \'{key}\' to \'{value}\' in "{file}"', end=printEnd())
    try:
        with open(file, 'r+') as f:
            try:
                data = json.loads(f.read())
                f.seek(0)
                data = searchAndReplace(data, key, value)

                json.dump(data, f, indent=4)
            finally:
                f.close()
    except ValueError:
        with open(file, 'r+', encoding='utf-8-sig') as f:
            try:
                data = json.loads(f.read())
                f.seek(0)
                data = searchAndReplace(data, key, value)

                json.dump(data, f, indent=4)
            finally:
                f.close()
    print('done!')


def searchAndReplace(var, searchKey, newValue):
    ''' Searches and replaces values in a dictionary with the specified key '''
    if type(var) == dict:
        for key in var.keys():
            if key == searchKey:
                var[key] = newValue
            elif type(var[key]) == dict:
                var[key] = searchAndReplace(var[key], searchKey, newValue)
        return var
    else:
        raise TypeError('Input not a dict (the only dicts are suported)')


def timeStamp(timeStart):
    return f'[{round(time.time()-timeStart, 3)}s]'


def printEnd():
    return '...    '



''' TODO:
        - Add some kind of better user input
'''


timeStart = time.time()
allZips = searchDirFor('./', '', '.zip')
displayArray(allZips, f'Found {len(allZips)} zips')


# Gets temporary directory
tempDir = './temp'
while os.path.isdir(tempDir) == 1:
    print(f'{timeStamp(timeStart)} Diractory "{tempDir}/" already exists, looking for new temp directory')
    tempDir += str(random.randint(0,9))

print(f'{timeStamp(timeStart)} Using temporary directory: "{tempDir}/"')


# Processes all the zip files
failed = [["Operation", "File", "Error type", "Error value"]]
for i in range(len(allZips)):
    # Get temporary current directory
    tempCurrentDir = os.path.join(tempDir, getFileName(allZips[i]))

    # Extract currently processing zip file
    print(f'\n{timeStamp(timeStart)} Extracting zip {i+1}: "{allZips[i]}" -> "{tempCurrentDir}/"', end=printEnd())
    with zipFile(allZips[i], 'r') as zip:
        try:
            zip.extractall(tempCurrentDir)
        except Exception as e:
            failed.append(["extracting", allZips[i], type(e).__name__, str(e)])
        finally:
            zip.close()
    print('done!')

    # Get JSON files of extracted zip
    allJsons = searchDirFor(tempCurrentDir, '', '.json')
    displayArray(allJsons, f'Found {len(allJsons)} jsons')

    # Look threw all JSONs and replace specefied thing
    for j in range(len(allJsons)):
        try:
            jsonChangeValue(allJsons[j], replaceSearchKey, replaceValueWith)
        except Exception as e:
            print("failed!")
            failed.append(["changing json", allJsons[j], type(e).__name__, str(e)])

    # Rezip extracted zip
    print(f'{timeStamp(timeStart)} Writing: "{tempCurrentDir}/*" -> "{allZips[i-1]}"', end=printEnd())
    with zipFile(allZips[i], 'w') as zip:
        try:
            for j in os.listdir(tempCurrentDir):
                zip.write(os.path.join(tempCurrentDir, j), arcname=j)
        except Excepton as e:
            failed.append(["zipping", os.path.join(tempCurrentDir, j), type(e).__name__, str(e)])
        finally:
            zip.close()
    print('done!')

    # Remove temp dir for zip
    print(f'{timeStamp(timeStart)} Removing: "{tempCurrentDir}"', end=printEnd())
    shutil.rmtree(tempCurrentDir)
    print('done!')


# Remove temp dir fully
print(f'\n{timeStamp(timeStart)} Removing the temp directory: "{tempDir}"', end=printEnd())
try:
    os.rmdir(tempDir)
    print('done!')
except Exception as e:
    print('failed!')
    failed.append(["removing", tempDir, type(e).__name__, str(e)])

print('\n'*2+'-='*5, 'SCRIPT FINISHED', '=-'*5+'\n')

if len(failed) > 1:
    temp = 'S' if len(failed)==1 else ''
    print(f'WITH ERROR{temp}'+'=-'*4)
    for i in range(len(failed)-1):
        print(f'\tGot {failed[i+1][2]} error "{failed[i+1][3]}" while {failed[i+1][0]} file "{failed[i+1][1]}"\n')

print(f'\nExecution of script took: {round(time.time()-timeStart, 6)} seconds\n')
